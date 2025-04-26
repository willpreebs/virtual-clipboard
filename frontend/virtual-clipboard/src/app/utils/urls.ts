export const toggleFolder = (url: string, userId: string, clipId: string, folderName: string) => {
    return `${url}/user/${userId}/clip/${clipId}/folder/${folderName}`;
}

export const getFolders = (url: string, userId: string) => {
    return `${url}/user/${userId}/folders`;
}

export const addFolderUrl = (url: string, userId: string, folderName: string) => {
    return `${url}/user/${userId}/addFolder/${folderName}`;
}