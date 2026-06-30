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

      // Generate a clean title (e.g., "sri_ganesha" -> "Sri Ganesha")
      let displayTitle = folder.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      
      // Create a consistent uppercase category key for filtering (e.g., "GANESHA")
      const categoryKey = displayTitle.toUpperCase();

      galleryData[categoryKey] = {
        title: displayTitle,
        folder: folder,
        images: files
      };
    }
  });

  res.status(200).json(galleryData);
}