"use client"

import { Box, IconButton, Input, InputBase, List, ListItem, ListItemButton, ListItemText } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import { useRef, useState } from "react";

type SidebarProps = {
  setFolder: (folderName: string) => void;
  folders: string[];
  addFolder: (folderName: string) => void;
  removeFolder: (folderName: string) => void;
}

export default function Sidebar({ setFolder, folders, addFolder, removeFolder }: SidebarProps) {
  console.log(folders)

  const [showInput, setShowInput] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // const [inputValue, setInputValue] = useState("");

  const handleClickOnAdd = () => {
    setShowInput(true);
    setTimeout(() => {
      inputRef.current?.focus();
    }, 0); 
  }

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && inputRef.current && inputRef.current.value.trim() !== "") {
      addFolder(inputRef.current.value);
      setShowInput(false);
    }
  };

  return (
    <Box
      className="w-60 h-screen bg-white border-r p-4"
      sx={{ display: { xs: "none", sm: "block" }, overflowY: "auto" }}
    >
      <h1 className="text-xl font-bold mb-6">oneClip</h1>
      <List>
        {folders.map((name, index) => (
          name && (
            <Box
              key={index}
              sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <ListItemButton
                className="rounded-xl mb-2 hover:bg-gray-100"
                onClick={() => setFolder(name)}>
                <ListItemText
                  primary={String(name)}
                  sx={{
                    color: "text.primary",
                    fontWeight: "medium",
                  }}
                />
              </ListItemButton>
              { name !== "All" && name !== "Favorites" &&
                <IconButton onClick={() => removeFolder(name)}>
                  <RemoveIcon />
                </IconButton>
              }
            </Box>
          )
        ))}
        {/* Add a button to add a new folder */}
        <ListItem sx={{pl: 0}}>
          <IconButton onClick={handleClickOnAdd}>
            <AddIcon/>
          </IconButton>
          {showInput && (
            <InputBase
              inputRef={inputRef}
              placeholder="New folder name"
              onKeyDown={handleInputKeyDown}
              onBlur={() => {
                if (inputRef.current?.value) {
                  addFolder(inputRef.current.value);
                }
                setShowInput(false);
              }}
              sx={{
                px: 1,
                py: 0.5,
                borderRadius: 1,
                backgroundColor: "transparent",
                "&:hover": {
                  backgroundColor: "#f3f4f6", // light gray (same as Tailwind's gray-100)
                },
                "& input": {
                  caretColor: "black", // Blinking cursor color
                },
              }}
            />
          )}
        </ListItem>
        
      </List>
    </Box>
  );
}
