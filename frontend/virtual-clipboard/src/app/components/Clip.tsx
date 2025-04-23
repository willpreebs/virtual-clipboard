import { Button, Card, CardContent, Typography } from "@mui/material";
import { Clipboard } from "./Clipboard";

type ClipProps = {
    clip: Clipboard;
};

export default function Clip({ clip }: ClipProps) {

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <Card sx={{ maxWidth: 345, m: 1 }}>

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
        </Card>
    )
}