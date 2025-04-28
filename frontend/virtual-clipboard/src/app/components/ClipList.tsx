import { Box } from "@mui/material";
import ClipboardItem from './ClipboardItem';
import { Clip } from "./Clipboard";

interface ClipListProps {
    clipboard: Clip[];
    toggleFavorite: (clip: Clip) => void;
}

export default function ClipList({ clipboard, toggleFavorite }: ClipListProps) {

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', m: 2 }}>
            {clipboard.map((clip, idx) => (
                <ClipboardItem key={idx} clip={clip} toggleFavorite={toggleFavorite} />
            ))}
        </Box>
    )

}