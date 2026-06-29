const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
  const imagesDir = path.join(process.cwd(), 'images');
  const galleryData = {};
  let allImages = []; // Array to hold every single image for the "ALL" view

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

      // Map the files to include their folder path so the frontend knows where to find them
      const localizedFiles = files.map(file => `${folder}/${file}`);
      allImages = allImages.concat(localizedFiles);

      galleryData[folder.toUpperCase().replace(/_/g, ' ')] = {
        title: folder.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
        folder: folder,
        images: files
      };
    }
  });

  // Add the master "ALL" category to the response
  galleryData["ALL"] = {
    title: "All Images",
    folder: "",
    images: allImages
  };

  res.status(200).json(galleryData);
}