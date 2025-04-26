"use client"

import { useEffect, useRef, useState } from 'react';

import { Card, Button, CardContent, Typography, Box } from '@mui/material';

import ClipForm from './ClipForm';

import Sidebar from './Sidebar';

import { toggleFavorite as togFav } from '../utils/urls';
import ClipList from './ClipList';

export type Clip = {
    text: string;
    time: string;
    id: string
}

export default function Clipboard() {

    const url_base = "localhost:8000"

    const [clipboard, setClipboard] = useState<Clip[]>([]);
    const [favorites, setFavorites] = useState<Clip[]>([]);

    const [folders, setFolders] = useState<string[]>([]);
    const [folder, setFolder] = useState<string | null>(null);

    const ws = useRef<WebSocket | null>(null);
    const user = useRef<string>("1");


    const toggleFavorite = (clip: Clip) => {
        setFavorites((prev) =>
            prev.includes(clip) ? prev.filter((i) => i !== clip) : [...prev, clip]
        );
        const url = togFav(url_base, user.current, clip.id);

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
    // console.log("Toggled favorite for: ", clip);
    // console.log("Favorites: ", favorites);

    };

    const getCurrentTime = () => {
        return new Date().toISOString()
    }

    useEffect(() => {
        ws.current = new WebSocket(`ws://${url_base}/user/${user.current || 1}/updateClipboard`);

        ws.current.onopen = () => {
            console.log('WebSocket connected');
            // ws.current?.send(JSON.stringify({ text: 'Hello from Next.js!', time: getCurrentTime() }));
            //   ws.current?.send("hello");
        };

        ws.current.onmessage = (event) => {
            try {
                console.log("received websocket event: ", event);
                const data: Clip[] = JSON.parse(event.data);
                setClipboard((prev) => [...prev, ...data]);
            } catch (err) {
                console.error("Failed to parse message:", event.data, err);
            }
        };

        return () => {
            ws.current?.close();
        };
    }, []);

    const postToClipboard = (clip: string) => {
        console.log("Posting: ", clip, " to clipboard")
        ws.current?.send(JSON.stringify({
            text: clip,
            time: getCurrentTime()
        }))
    }

    // Function to copy text to the clipboard


    return (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Sidebar />
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px', margin: '20px', fontSize: '20' }}>
                <Typography variant="h3" className='font-semibold'>
                    Clipboard History
                </Typography>
                <ClipList clipboard={clipboard} toggleFavorite={toggleFavorite} favorites={favorites} />
            </Box>

            <ClipForm postToClipboard={postToClipboard} />
        </Box>

    );
}
