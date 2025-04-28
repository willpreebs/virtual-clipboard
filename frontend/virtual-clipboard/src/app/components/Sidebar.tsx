"use client"

import { Box, IconButton, List, ListItemButton, ListItemText } from "@mui/material";
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';

type SidebarProps = {
  setFolder: (folderName: string) => void;
  folders: string[];
  addFolder: (folderName: string) => void;
  removeFolder: (folderName: string) => void;
}

export default function Sidebar({ setFolder, folders, addFolder, removeFolder }: SidebarProps) {
  console.log(folders)
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
        <ListItemButton
          className="rounded-xl mb-2 hover:bg-gray-100"
          onClick={() => {
            const folderName = prompt("Enter folder name:");
            if (folderName) {
              addFolder(folderName);
            }
          }}
        >
          <IconButton size="medium"><AddIcon /></IconButton>
        </ListItemButton>
      </List>
    </Box>
  );
}
