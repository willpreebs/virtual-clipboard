

import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';

interface ClipFormProps {
    postToClipboard: (text: string) => void;
}

const ClipForm: React.FC<ClipFormProps> = ({ postToClipboard }) => {

    const [input, setInput] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() !== '') {
            postToClipboard(input);
            setInput('');
        }
    };

    return (
        <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                width: '100%',
                maxWidth: 400,
                margin: '0 auto',
            }}
        >
            <TextField
                label="Enter new clip"
                variant="outlined"
                value={input}
                onChange={(e) => setInput(e.target.value)}
            />
            <Button type="submit" variant="contained" color="primary">
                Clip
            </Button>
        </Box>
    );
};

export default ClipForm;