const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
    const imagesDir = path.join(process.cwd(), 'images');
    const galleryData = {};

    if (!fs.existsSync(imagesDir)) {
        return res.status(404).json({ error: "Images directory not found" });
    }

    const folders = fs.readdirSync(imagesDir);
    folders.forEach(folder => {
        const folderPath = path.join(imagesDir, folder);
        if (fs.statSync(folderPath).isDirectory()) {
            const files = fs.readdirSync(folderPath).filter(file => 
                /\.(jpg|jpeg|png|gif|webp)$/i.test(file)
            );
            
            galleryData[folder.toUpperCase().replace(/_/g, ' ')] = {
                title: folder.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
                folder: folder,
                images: files
            };
        }
    });

    // Returns fresh folders live on every refresh
    res.status(200).json(galleryData);
}