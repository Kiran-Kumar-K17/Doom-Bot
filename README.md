# 🤖 Iron Doom Jarvis

**Your Autonomous AI Assistant for Ultimate Productivity**

Iron Doom Jarvis is a self-updating, continuously learning Discord bot that serves as your personal AI assistant for productivity, learning, and entertainment. It automatically fetches new content, learns your preferences, and provides personalized recommendations 24/7.

![Iron Doom Jarvis](https://img.shields.io/badge/Iron%20Doom-Jarvis-red?style=for-the-badge&logo=discord)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Discord](https://img.shields.io/badge/Discord-Bot-5865F2?style=for-the-badge&logo=discord)

## 🌟 Features

### 🧠 **Autonomous Learning**
- **Self-Updating Content**: Automatically fetches YouTube videos, books, and news daily
- **Preference Learning**: Learns your interests and adapts recommendations over time
- **Smart Recommendations**: AI-powered suggestions based on your behavior patterns

### 📋 **Task Management**
- **Notion Integration**: Sync with Notion databases for seamless task management
- **Smart Prioritization**: Automatically adjusts task priorities based on deadlines
- **Progress Tracking**: Monitor completion rates and productivity streaks
- **Automated Reminders**: Get notified about overdue tasks during work hours

### 📚 **Learning Assistant**
- **YouTube Integration**: Search and track educational videos with preference learning
- **Book Recommendations**: Discover books based on your reading history and interests
- **News Aggregation**: Stay updated with tech news and industry trends
- **Learning Paths**: Get structured approaches to learn new topics

### 💪 **Fitness & Wellness**
- **Workout Logging**: Track exercise sessions and estimate calories burned
- **Fitness Statistics**: Monitor your workout patterns and progress
- **Focus Sessions**: Pomodoro timer for productivity with motivational messages

### 🎯 **AI Assistant**
- **Smart Q&A**: Get advice on productivity, learning, coding, and career development
- **Personalized Suggestions**: Receive recommendations based on your activity patterns
- **Pattern Analysis**: Understand your learning and productivity trends

### 🎮 **Entertainment**
- **Motivational Quotes**: Daily inspiration from tech leaders and innovators
- **Programming Jokes**: Light-hearted humor for developers
- **Interactive Games**: Dice rolls, coin flips, magic 8-ball, and more

### 📊 **Analytics**
- **Comprehensive Stats**: Track all aspects of your productivity and learning
- **Trend Analysis**: Understand your patterns and optimize your schedule
- **Goal Management**: Set, track, and celebrate achieving your goals
- **Performance Insights**: Get data-driven insights about your progress

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- (Optional) API keys for enhanced features

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/iron-doom-jarvis.git
   cd iron-doom-jarvis
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure your API keys**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys
   ```

4. **Start the bot**
   ```bash
   python iron_doom_jarvis.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f iron-doom-jarvis
   ```

## 🔧 Configuration

### Required API Keys

| Service | Required | Purpose |
|---------|----------|---------|
| **Discord Bot Token** | ✅ Yes | Core bot functionality |
| **Primary Channel ID** | ✅ Yes | Main communication channel |

### Optional API Keys (Recommended)

| Service | Purpose | How to Get |
|---------|---------|------------|
| **Notion Token** | Task management | [Notion Integrations](https://www.notion.so/my-integrations) |
| **YouTube API Key** | Video recommendations | [Google Cloud Console](https://console.cloud.google.com/) |
| **Google Books API** | Book recommendations | [Google Cloud Console](https://console.cloud.google.com/) |
| **News API Key** | Tech news aggregation | [NewsAPI.org](https://newsapi.org/) |
| **GitHub Token** | Repository tracking | [GitHub Settings](https://github.com/settings/tokens) |
| **OpenAI API Key** | Enhanced AI features | [OpenAI Platform](https://platform.openai.com/) |

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here
PRIMARY_CHANNEL_ID=your_primary_channel_id_here

# Optional but recommended
NOTION_TOKEN=your_notion_integration_token_here
NOTION_TASK_DATABASE_ID=your_notion_task_database_id_here
YOUTUBE_API_KEY=your_youtube_api_key_here
GOOGLE_BOOKS_API_KEY=your_google_books_api_key_here
NEWS_API_KEY=your_news_api_key_here
GITHUB_TOKEN=your_github_token_here
GITHUB_USERNAME=your_github_username_here
OPENAI_API_KEY=your_openai_api_key_here
```

## 🎮 Commands Reference

### 📋 Task Management
- `!today` - Show today's agenda with tasks and recommendations
- `!tasks [filter]` - Show pending tasks (all/today/overdue)
- `!addtask <title> | <description> | <priority> | <due_date>` - Add new task
- `!stats` - Show productivity statistics
- `!remind <time> <message>` - Set a reminder (30m, 2h, 1d)
- `!focus [duration]` - Start a focus session with Pomodoro timer

### 📚 Learning & Content
- `!recommend [type]` - Get personalized recommendations (all/video/book/news)
- `!youtube <query>` - Search YouTube videos and track viewing
- `!books <query>` - Search books and add to reading list
- `!news [category]` - Get latest tech news
- `!learn <topic>` - Get structured learning path for a topic
- `!interests [action] [topics]` - Manage learning interests

### 💪 Fitness & Health
- `!workout <type> <duration> [notes]` - Log workout session
- `!fitness` - Show fitness statistics
- `!workouts [limit]` - Show recent workouts

### 🤖 AI Assistant
- `!ask <question>` - Ask AI assistant for advice
- `!suggest` - Get personalized suggestions based on activity
- `!analyze` - Analyze your learning patterns
- `!brainstorm <topic>` - Generate creative ideas

### 🎮 Fun & Entertainment
- `!quote` - Get inspirational quote
- `!joke` - Get programming joke
- `!fact` - Get interesting tech fact
- `!motivate` - Get pumped with motivation
- `!roll [sides]` - Roll dice
- `!coinflip` - Flip a coin
- `!8ball <question>` - Magic 8-ball
- `!choose <option1, option2, ...>` - Choose between options

### 📊 Analytics & Stats
- `!mystats` - Comprehensive personal statistics
- `!trends` - Show activity trends over time
- `!compare [period]` - Compare performance across time periods
- `!goals [action] [goal]` - Manage personal goals
- `!leaderboard` - Show productivity leaderboard

## 🔄 Automated Features

### Daily Routines

- **6:00 AM UTC**: Fetch fresh news and update task priorities
- **7:00 AM UTC**: Fetch new YouTube content based on preferences
- **8:00 AM UTC**: Update book recommendations
- **8:00 PM UTC**: Send evening summary with accomplishments
- **Hourly (9 AM - 6 PM)**: Check for overdue tasks and send reminders
- **Weekly**: Generate performance reports and insights

### Continuous Learning

- **Content Pool Updates**: Automatically refreshes recommendations based on APIs
- **Preference Tracking**: Learns from your interactions and feedback
- **Adaptive Suggestions**: Improves recommendations over time
- **History Tracking**: Maintains comprehensive interaction history

## 📁 Project Structure

```
iron-doom-jarvis/
├── iron_doom_jarvis.py        # Main bot with scheduler
├── commands/                  # Discord command modules
│   ├── tasks.py              # Task management commands
│   ├── learning.py           # Learning and content commands  
│   ├── fitness.py            # Fitness tracking commands
│   ├── ai_assistant.py       # AI assistant commands
│   ├── fun.py                # Entertainment commands
│   └── stats.py              # Analytics and stats commands
├── services/                  # API service integrations
│   ├── notion_service.py     # Notion API integration
│   ├── youtube_service.py    # YouTube Data API
│   ├── books_service.py      # Google Books API
│   ├── news_service.py       # News API integration
│   └── github_service.py     # GitHub API integration
├── models/                    # ML and data models
│   └── preference_model.py   # Preference learning engine
├── utils/                     # Utility functions
│   ├── helpers.py            # General utilities
│   └── logger.py             # Logging configuration
├── data/                      # Data storage
│   ├── history.json          # User interaction history
│   ├── youtube_preferences.json
│   ├── book_preferences.json
│   └── news_preferences.json
├── logs/                      # Application logs
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose setup
├── setup.sh                   # Setup script
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🚀 Deployment Options

### Local Development

```bash
# Clone and setup
git clone <repository-url>
cd iron-doom-jarvis
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run locally
python iron_doom_jarvis.py
```

### Docker Deployment

```bash
# Basic deployment
docker-compose up -d

# With dashboard (optional)
docker-compose --profile dashboard up -d

# View logs
docker-compose logs -f
```

### Cloud Deployment

#### AWS ECS / Azure Container Instances / Google Cloud Run

1. Build and push Docker image
2. Configure environment variables
3. Deploy container with persistent storage for data/logs

#### VPS/Dedicated Server

1. Install Docker and Docker Compose
2. Clone repository and configure `.env`
3. Run with `docker-compose up -d`
4. Setup reverse proxy (nginx) if needed

## 🛠️ Development

### Setting up Development Environment

```bash
# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

### Adding New Features

1. **Commands**: Add new command files in `commands/` directory
2. **Services**: Add API integrations in `services/` directory  
3. **Models**: Add data models and ML logic in `models/` directory
4. **Utils**: Add utility functions in `utils/` directory

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 🔒 Security

- **API Keys**: Store all sensitive data in environment variables
- **Data Privacy**: All user data is stored locally (not shared with external services)
- **Rate Limiting**: Built-in rate limiting for all API calls
- **Error Handling**: Comprehensive error handling and logging

## 📊 Performance

- **Memory Usage**: ~50-100MB typical usage
- **CPU Usage**: Low CPU usage with event-driven architecture  
- **Storage**: ~10-50MB for data and logs
- **API Calls**: Optimized to stay within rate limits of all services

## 🐛 Troubleshooting

### Common Issues

#### Bot not responding
- Check Discord token is valid
- Verify bot has necessary permissions in server
- Check logs for connection errors

#### API features not working
- Verify API keys are correct in .env file
- Check API key permissions and quotas
- Review service-specific logs

#### Scheduled tasks not running
- Check system timezone settings
- Verify APScheduler configuration
- Look for scheduler errors in logs

### Getting Help

1. Check the logs in `logs/` directory
2. Review configuration in `.env` file
3. Consult API documentation for specific services
4. Open an issue on GitHub with logs and configuration details

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Discord.py** - Excellent Python Discord library
- **APScheduler** - Robust job scheduling
- **All API Providers** - Notion, YouTube, Google Books, NewsAPI, GitHub
- **Open Source Community** - For inspiration and tools

## 🔮 Roadmap

- [ ] **Mobile App**: Native mobile companion app
- [ ] **Voice Commands**: Voice interaction via Discord voice channels
- [ ] **Advanced ML**: More sophisticated recommendation algorithms
- [ ] **Team Features**: Multi-user support and team collaboration
- [ ] **Integration Hub**: Connect with more productivity services
- [ ] **Custom Dashboards**: Web-based analytics dashboard
- [ ] **Plugin System**: Allow custom user plugins

---

**Built with ❤️ by the Iron Doom Jarvis Team**

*"Your autonomous AI assistant for ultimate productivity and continuous learning"*

## 🚀 Ready to Get Started?

1. **Star this repository** ⭐
2. **Run the setup script**: `./setup.sh`
3. **Configure your API keys** in `.env`
4. **Launch your Iron Doom Jarvis**: `python iron_doom_jarvis.py`

Welcome to the future of autonomous productivity assistance! 🤖💪