"use client"

import { Button, Card, CardContent, IconButton, Typography } from "@mui/material";
import { Clip } from "./Clipboard";
import { Star, StarBorder } from "@mui/icons-material";

type ClipProps = {
    clip: Clip;
    toggleFavorite: (clip: Clip) => void;
    favorites: Clip[];
};

export default function ClipboardItem({ clip, toggleFavorite }: ClipProps) {

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <Card sx={{ width: 345, m: 1 }}>

            {/* Card Content (Text and other content) */}
            <CardContent>
                <Typography variant="body2" color="text.secondary">
                    {clip.text}
                </Typography>
            </CardContent>

            {/* Card Actions (Optional buttons or actions) */}
            <Button size="small" color="primary" onClick={() => copyToClipboard(clip.text)}>
                Copy
            </Button>
            <IconButton onClick={() => toggleFavorite(clip)}>
                {clip.favorite ? <Star /> : <StarBorder />}
            </IconButton>
        </Card>
    )
}