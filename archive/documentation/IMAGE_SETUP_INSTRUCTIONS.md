# Quiz Topology Images Setup Instructions

## Images to Save

You need to save the two network topology images to the following location:
`c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\images\topology\`

### Image 1: BUS Topology
- **Filename:** `bus-topology.jpg`
- **Description:** The first image showing computers connected to a network backbone (horizontal line)
- **Full path:** `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\images\topology\bus-topology.jpg`

### Image 2: RING Topology  
- **Filename:** `ring-topology.jpg`
- **Description:** The second image showing computers connected in a circular/ring formation
- **Full path:** `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\images\topology\ring-topology.jpg`

## How to Save the Images

1. Open each image from your chat attachments
2. Right-click on the image
3. Select "Save Image As..."
4. Navigate to: `c:\Users\gilbe\OneDrive\Desktop\RiddleNet\static\images\topology\`
5. Save the first image as `bus-topology.jpg`
6. Save the second image as `ring-topology.jpg`

## Verify Setup

After saving the images, refresh the quiz page at: http://127.0.0.1:5001/quiz/

The topology questions should now display the images above the multiple choice options.

## What Was Changed

✅ Added CSS styling for question images with hover effects
✅ Updated quiz questions to include image URLs
✅ Modified JavaScript to render images when available
✅ Added responsive mobile styling for images
✅ Enhanced Bus Topology question with image
✅ Enhanced Ring Topology question with image

## Features

- Images have a nice border and shadow effect
- Images scale on hover for better viewing
- Images are responsive and work on mobile devices
- Images only show when defined in the question object
