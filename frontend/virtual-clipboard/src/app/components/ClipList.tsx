import { Box } from "@mui/material";
import ClipboardItem from './ClipboardItem';
import { Clip } from "./Clipboard";

interface ClipListProps {
    clipboard: Clip[];
    toggleFavorite: (clip: Clip) => void;
    favorites: Clip[]; // Replace 'any' with the specific type of your favorites
}

export default function ClipList({ clipboard, toggleFavorite, favorites }: ClipListProps) {

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', m: 2 }}>
            {clipboard.map((clip, idx) => (
                <ClipboardItem key={idx} clip={clip} toggleFavorite={toggleFavorite} favorites={favorites} />
            ))}
        </Box>
    )

}