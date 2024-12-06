# 🎥 Video Search and Upload Bot Assignment

A Python-based bot that searches, downloads, and uploads videos from social media platforms.

## Installation

1. Clone the repository
2. Install dependencies using `pip install -r requirements.txt`.

## 🎯 Objective

Create a bot to download videos from Instagram, TikTok, and Reddit, then upload them to our server using provided APIs.

## 📋 Requirements

### Core Features

- Search and download videos from specified platforms
- Upload videos via API endpoints
- Auto-delete local files after upload
- Monitor /videos directory for new .mp4 files
- Async operations for concurrent uploads

### API Integration

1. Get Upload URL:

```
Endpoint: https://api.socialverseapp.com/posts/generate-upload-url
Headers: {
    "Flic-Token": "<YOUR_TOKEN>",
    "Content-Type": "application/json"
}
```

2. Upload Video:

- Use pre-signed URL with PUT request

3. Create Post:

```
Endpoint: https://api.socialverseapp.com/posts
Headers: {
    "Flic-Token": "<YOUR_TOKEN>",
    "Content-Type": "application/json"
}
Body: {
    "title": "<video title>",
    "hash": "<hash from Step 1>",
    "is_available_in_public_feed": false,
    "category_id": <category_id>
}
```

### Technical Requirements

- Python
- asyncio for concurrent operations
- tqdm for progress bars
- Error handling
- Directory monitoring

## 📁 Basic Project Structure

```
video-bot/
├── main.py                # Main script
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

## 📝 Submission Guidelines

### Code Repository

- Complete GitHub repository
- Clear documentation
- Proper code structure
- Detailed README.md

### Video Presentation (5 min max)

- Project setup instructions
- Code walkthrough
- Self-introduction
- Submit via Internshalla/Google Drive

## 📊 Evaluation Criteria

### Code Quality (30%)

- Organization and structure
- Readability
- Performance optimization
- Best practices implementation

### Functionality (40%)

- Video search implementation
- Upload mechanism
- Error handling
- Feature completeness

### Documentation (15%)

- Setup instructions
- Usage guidelines
- Code comments
- README quality

### Presentation (15%)

- Clear explanation
- Technical understanding
- Time management

## ✅ Verification

1. Download Empowerverse App ([Android](https://play.google.com/store/apps/details?id=com.empowerverse.app) | [iOS](https://apps.apple.com/us/app/empowerverse/id6449552284))
2. Navigate to "Super Feed" category
3. Hold category and click Browse
4. Check uploaded videos

For Flic-Token access, message on [Telegram](https://t.me/+vKzmXhW1Epw0Mzll) with your Empowerverse username.

Results will be announced within 24 hours of submission.
