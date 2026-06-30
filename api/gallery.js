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

      let displayTitle = folder.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      
      if (displayTitle === "Sri Ganesha") displayTitle = "Ganesha";
      if (displayTitle === "Radhe Krishna") displayTitle = "Radhe";

      const categoryKey = displayTitle.toUpperCase();

      // Map each file into an object containing both the filename AND a unique description
      const imagesWithDescriptions = files.map(file => {
        let imageDesc = `A beautiful depiction of ${displayTitle}.`;

        // EXAMPLE: Customizing by specific file names
        if (file === 'radhe_flute.jpg') {
          imageDesc = "Radhe listening intently to the divine melody of the flute.";
        } else if (file === 'ganesha_sitting.png') {
          imageDesc = "Lord Ganesha seated majestically on his golden throne.";
        } else if (categoryKey === "RADHE") {
          imageDesc = "Epitome of eternal love and divine grace.";
        }

        return {
          filename: file,
          description: imageDesc
        };
      });

      galleryData[categoryKey] = {
        title: displayTitle,
        folder: folder,
        images: imagesWithDescriptions // Now an array of objects
      };
    }
  });

  res.status(200).json(galleryData);
}