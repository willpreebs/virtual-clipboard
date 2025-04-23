"use client"

import { useEffect, useRef, useState } from 'react';

import { Card, Button, CardContent, Typography } from '@mui/material';
import Clip from './Clip';
import ClipForm from './ClipForm';

export type Clipboard = {
    text: string;
    time: string;
}

export default function Clipboard() {

    const [clipboard, setClipboard] = useState<Clipboard[]>([]);
    const ws = useRef<WebSocket | null>(null);
    const user = useRef<number>(1);

    const getCurrentTime = () => {
        return new Date().toISOString()
    }

    useEffect(() => {
        ws.current = new WebSocket(`ws://localhost:8000/user/${user.current || 1}/updateClipboard`);

        ws.current.onopen = () => {
            console.log('WebSocket connected');
            ws.current?.send(JSON.stringify({ text: 'Hello from Next.js!', time: getCurrentTime() }));
            //   ws.current?.send("hello");
        };

        ws.current.onmessage = (event) => {
            try {
                console.log("received websocket event: ", event);
                const data: Clipboard[] = JSON.parse(event.data);
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
        <div style={{ display: 'flex'}}>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '20px', margin: '20px' }}>

            {clipboard.map((clip, idx) => (
                <Clip key={idx} clip={clip}/>
            ))}
            </div>

            <ClipForm postToClipboard={postToClipboard}/>
        </div>
        
    );
}
