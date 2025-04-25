"use client"

import { useEffect, useRef, useState } from 'react';

import { Card, Button, CardContent, Typography, Box } from '@mui/material';
import ClipboardItem from './Clip';
import ClipForm from './ClipForm';

import Sidebar from './Sidebar';

export type Clip = {
    text: string;
    time: string;
}

export default function Clipboard() {

    const [clipboard, setClipboard] = useState<Clip[]>([]);
    const [favorites, setFavorites] = useState<Clip[]>([]);

    const ws = useRef<WebSocket | null>(null);
    const user = useRef<number>(1);


    const toggleFavorite = (clip: Clip) => {
        setFavorites((prev) =>
            prev.includes(clip) ? prev.filter((i) => i !== clip) : [...prev, clip]
        );
    };

    const getCurrentTime = () => {
        return new Date().toISOString()
    }

    useEffect(() => {
        ws.current = new WebSocket(`ws://localhost:8000/user/${user.current || 1}/updateClipboard`);

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
                <Box sx={{ display: 'flex', flexDirection: 'column', m: 2}}>
                    {clipboard.map((clip, idx) => (
                        <ClipboardItem key={idx} clip={clip} toggleFavorite={toggleFavorite} favorites={favorites}/>
                    ))}
                </Box>
            </Box>

            <ClipForm postToClipboard={postToClipboard} />
        </Box>

    );
}
