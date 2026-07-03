const fs = require('fs');
const path = require('path');

export default function handler(req, res) {
    const imagesDir = path.join(process.cwd(), 'images');
    const descriptionsPath = path.join(process.cwd(), 'api', 'descriptions.json');
    const galleryData = {};

    if (!fs.existsSync(imagesDir)) {
        return res.status(404).json({ error: "Images directory not found" });
    }

    // Load our newly generated computer vision static database mapping layer
    let aiDescriptions = {};
    if (fs.existsSync(descriptionsPath)) {
        try {
            aiDescriptions = JSON.parse(fs.readFileSync(descriptionsPath, 'utf8'));
        } catch (e) {
            console.error("Failed to parse descriptions database file", e);
        }
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

            // Map files into structural components with automated descriptions
            const imagesWithDescriptions = files.map(file => {
                const lookupKey = `${folder}/${file}`;
                
                // Fetch the AI description; fallback cleanly to standard string template if not indexed yet
                const imageDesc = aiDescriptions[lookupKey] || `A beautiful depiction of ${displayTitle}.`;

                return {
                    filename: file,
                    description: imageDesc
                };
            });

            galleryData[categoryKey] = {
                title: displayTitle,
                folder: folder,
                images: imagesWithDescriptions
            };
        }
    });

    res.status(200).json(galleryData);
}