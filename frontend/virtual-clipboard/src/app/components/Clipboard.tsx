"use client"

import { useEffect, useRef, useState } from 'react';

import { Card, Button, CardContent, Typography, Box } from '@mui/material';

import ClipForm from './ClipForm';

import Sidebar from './Sidebar';

import { addFolderUrl, getFolders, toggleFolder } from '../utils/urls';
import ClipList from './ClipList';

export type Clip = {
    text: string;
    time: string;
    id: string
    favorite: boolean
}

export default function Clipboard() {

    const url_base = "http://localhost:8000"

    const websocket_base = "ws://localhost:8000"

    const [clipboard, setClipboard] = useState<Clip[]>([]);

    const [folders, setFolders] = useState<string[]>(["All", "Favorites"]);
    const [folder, setFolder] = useState<string>("All"); // shows All folder by default
    const [user, setUser] = useState<string>("1");

    const folderCache = useRef<{ [key: string]: Clip[] }>({});

    const getCachedFolderContents = async (folderName: string) => {
        if (folderCache.current[folderName]) {
            console.log(`Cache hit for folder: ${folderName}`);
            return folderCache.current[folderName];
        }
        console.log(`Cache miss for folder: ${folderName}`);
        const contents = await getFolderContents(folderName);
        folderCache.current[folderName] = contents;
        return contents;
    };

    useEffect(() => {
        if (folder) {
            getCachedFolderContents(folder).then((contents) => {
                setClipboard(contents);
            });
        }
    }, [folder]);

    const socket = useRef<WebSocket | null>(null);
    // set folders
    useEffect(() => {
        fetch(getFolders(url_base, user), {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                console.log('Success:', data);
                // set folders to an array of the name of the folders
                setFolders(["All", "Favorites",
                    ...data.folders.map((folder: { name: string }) => { folder.name }).filter((name: string) => name !== "Favorites")]);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }, [user]);

    // // handle folder change
    // useEffect(() => {
    //     if (folder) {
    //         console.log("Folder changed to: ", folder);
    //         getFolderContents(folder).then((contents) => {
    //             setClipboard(contents);
    //         });
    //     }
    // }, [folder]);


    useEffect(() => {

        socket.current = new WebSocket(`${websocket_base}/user/${user || 1}/updateFolder/${folder}`);

        socket.current.onopen = () => {
            console.log('WebSocket opened');
        };

        socket.current.onmessage = (event) => {
            try {
                console.log("received websocket event: ", event);

                const data: Clip[] | Clip = JSON.parse(event.data);
                if (Array.isArray(data)) {
                    setClipboard(data);
                }
                else {
                    setClipboard((prev) => [data, ...prev]);
                }
            } catch (err) {
                console.error("Failed to parse message:", event.data, err);
            }
        };

        socket.current.onclose = () => {
            console.log('WebSocket closed');
        }

        return () => {
            socket.current?.close();
        };
    }, [folder]);

    const toggleFavorite = (clip: Clip) => {

        clip.favorite = !clip.favorite;
        const url = toggleFolder(url_base, user, clip.id, "Favorites");

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            // body: JSON.stringify)
        })
            .then((response) => {
                console.log("response: ", response);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            }
            )
            .then((data) => {
                console.log('Success:', data);
            }
            )
            .catch((error) => {
                console.error('Error:', error);
            }
            );
    };

    const addToFolder = (clip: Clip, folderName: string) => {
        const url = toggleFolder(url_base, user, clip.id, folderName);
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    const getCurrentTime = () => {
        return new Date().toISOString()
    }


    const postToClipboard = (clip: string) => {
        console.log("Posting: ", clip, " to clipboard")
        if (socket.current) {
            console.log("Posting to folder: ", folder);
            socket.current.send(JSON.stringify({
                text: clip,
                time: getCurrentTime()
            }))
        }
    }

    const addFolder = (folderName: string) => {
        setFolders((prev) => [...prev, folderName]);
        fetch(addFolderUrl(url_base, user, folderName), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }

    const getFolderContents = async (folderName: string) => {
        const url = `${url_base}/user/${user}/folder/${folderName}`;
        const contents: Clip[] = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                console.log('Success:', data);
                return data;
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        return contents;
    }

    const isFolderEmpty = async (folderName: string) => {
        const contents = await getFolderContents(folderName);
        return contents.length === 0;
    }

    const removeFolder = async (folderName: string) => {
        // if folder is not empty, send warning message to user
        if (!await isFolderEmpty(folderName)) {
            // TODO: ask user for confirmation
            alert("Folder is not empty. Please empty the folder before deleting it.");
            return;
        }

        setFolders((prev) => prev.filter((folder) => folder !== folderName));
        const url = `${url_base}/user/${user}/removeFolder/${folderName}`;
        fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then((data) => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });

        // If this folder is the current folder, set folder to null
        if (folder === folderName) {
            setFolder("All");
        }
    }

    return (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Sidebar setFolder={setFolder} folders={folders} removeFolder={removeFolder} addFolder={addFolder} />
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', padding: '20px', margin: '20px', fontSize: '20' }}>
                <Typography variant="h3" className='font-semibold'>
                    {folder === "All" ? "Clipboard" : folder}
                </Typography>
                <ClipList clipboard={clipboard} toggleFavorite={toggleFavorite} />
            </Box>

            <ClipForm postToClipboard={postToClipboard} />
        </Box>

    );
}
