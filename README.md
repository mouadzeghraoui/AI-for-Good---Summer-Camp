# Cinema Agent Lab - IBM watsonx Orchestrate Hands-on Workshop

Welcome to this hands-on lab where you'll build and deploy a complete cinema booking agent using IBM watsonx Orchestrate. This lab will take you through the entire process of creating an intelligent agent that can help users discover movies, find showtimes, and book tickets.

## Lab Objectives

By the end of this lab, you will:
- Understand how to import Python tools into watsonx Orchestrate
- Configure API connections for external services
- Create and deploy an intelligent agent with multiple tools
- Test real-world scenarios including movie discovery and ticket booking

## Prerequisites

- Access to IBM watsonx Orchestrate
- Basic understanding of Python (reading comprehension)
- Terminal/Command line access
- IDE (e.g., VS Code)

## Lab Setup

### 1. Clone the Lab Repository

```bash
git clone [YOUR_GITHUB_REPO_URL]
cd cinema-agent-lab
```

### 2. Verify Lab Contents

Your lab directory should contain:

```
cinema-agent-lab/
├── tools/python/                    # Python tools for the agent
│   ├── movie_search_tool/
│   ├── cinema_tool/
│   └── booking_tool/
├── agents/cinema_agent.yaml         # Agent configuration
├── setup-connections.sh             # API key setup script
├── import-all.sh                   # Tool import script
└── .env                            # API credentials (pre-configured)
```

---

## Part 1: Understanding the Tools

Before importing tools into watsonx Orchestrate, let's examine what we're working with.

### Tool Overview

Our cinema agent uses three main Python tools:

#### 1. Movie Search Tool (movie_search_tool_v2.py)
- Searches for movies by genre, title, or popularity
- Gets detailed movie information (cast, director, ratings)
- Provides movie recommendations

#### 2. Cinema Tool (cinema_tool_v2.py)
- Finds cinemas near a location
- Gets showtimes for specific movies
- Searches for films in cinema databases

#### 3. Booking Tool (booking_tool.py)
- Checks seat availability
- Creates bookings with customer details
- Processes payments (simulated)

### Explore a Tool

Open `tools/python/movie_search_tool/source/movie_search_tool_v2.py` and examine the structure:

```python
@tool
def search_movies(query: str = "", 
                  status: str = "now_playing",
                  genre: str = "",
                  region: str = "FR") -> Dict[str, Any]:
```

Notice:
- The `@tool` decorator that makes this function available to watsonx Orchestrate
- Type hints that help the platform understand parameters
- Clear documentation strings

---

## Part 2: Setting Up API Connections

Our tools need to connect to external APIs. watsonx Orchestrate handles this through its connection system.

### API Services Used
- **TMDb (The Movie Database)**: Global movie information
- **MovieGlu**: Real cinema showtimes and booking data

### Configure API Connections

Run the automated setup script:

```bash
./setup-connections.sh
```

This script will:
1. Create `tmdb_api` connection with TMDb credentials
2. Create `movieglu_api` connection with MovieGlu credentials
3. Configure them for the draft environment

Verify connections:
```bash
orchestrate connections list
```

You should see both `tmdb_api` and `movieglu_api` in the output.

---

## Part 3: Importing Tools into watsonx Orchestrate

Now we'll import our Python tools into the platform.

### Import Tools

Run the import script:

```bash
./import-all.sh
```

This script imports:
1. Movie Search Tools (3 functions)
2. Cinema Tools (4 functions)
3. Booking Tools (4 functions)
4. Cinema Agent configuration

Verify tool import:
```bash
orchestrate tools list
```

Expected output should show 11 imported tools:
- `search_movies`
- `get_movie_details`
- `get_movie_recommendations`
- `find_cinemas_nearby`
- `get_cinema_showtimes`
- `search_film_by_title`
- `check_film_showtimes`
- `check_seat_availability`
- `create_booking`
- `process_payment`
- `get_booking_status`

---

## Part 4: Understanding the Agent Configuration

Let's examine how our agent is configured.

### Analyze Agent Configuration

Open `agents/cinema_agent.yaml`:

**Key Components:**
- **LLM Model**: `watsonx/mistralai/mistral-large`
- **Style**: `react` (allows tool usage and reasoning)
- **Tools**: All 11 imported tools
- **Instructions**: Detailed guidelines for behavior

**Important Instructions:**

**Tool Usage Guidelines:**
- When user asks "what movies are playing": ONLY use `search_movies` and STOP
- Only use additional tools when user specifically asks for showtimes, cinemas, or bookings
- NEVER combine movie search with cinema/showtime search unless explicitly requested

---

## 🎬 Part 5: Testing Scenarios

Now let's test our agent with real-world scenarios.

### Movie Discovery Scenario

**Test Scenario 1: Basic Movie Search**

Ask the agent:
> "What sci-fi movies are playing this weekend?"

**Expected Behavior:**

1. ✅ Agent uses ONLY `search_movies` tool
2. ✅ Shows list of sci-fi movies
3. ✅ Asks if you want more information
4. ❌ Does NOT automatically search for showtimes

**Sample Response:**
> Here are the sci-fi movies currently playing:
>
> 1. Jurassic World Rebirth (Rating: 6.5)
> 2. 28 Years Later (Rating: 7.2)
> 3. M3GAN 2.0 (Rating: 7.2)
> 4. Superman (Rating: 5.7)
> 5. Elio (Rating: 6.8)
>
> Would you like showtimes for any of these movies?

### Showtime Discovery Scenario

**Test Scenario 2: Finding Showtimes**

Continue with:
> "Show me showtimes for M3GAN 2.0 in Paris"

**Expected Behavior:**
1. ✅ Agent uses `search_film_by_title` to get MovieGlu film ID
2. ✅ Uses `check_film_showtimes` to find cinemas showing the movie
3. ✅ Displays cinemas with showtime counts

**Sample Response:**
> Here are cinemas showing M3GAN 2.0 in Paris:
>
> - UGC Ciné Cité Les Halles (0.6 km) - 2 showtimes
> - Pathé Parnasse Premium (1.6 km) - 1 showtime
> - MK2 Bibliothèque (2.1 km) - 2 showtimes
>
> Would you like specific times for any cinema?

### Specific Showtime Scenario

**Test Scenario 3: Getting Specific Times**

Continue with:
> "What are the specific times at UGC Ciné Cité Les Halles?"

**Expected Behavior:**
1. ✅ Agent uses `get_cinema_showtimes` with correct cinema ID
2. ✅ Shows specific screening times

### Booking Scenario

**Test Scenario 4: Complete Booking Flow**

Try this realistic booking request:
> "book a seat for elio movie at 13:30"

**Expected Behavior:**
1. ✅ Agent requests customer information (name, email, cinema)
2. ✅ Validates showtime availability
3. ✅ Offers alternative times if requested time unavailable
4. ✅ Creates booking confirmation with details

**Sample Interaction:**
```
User: "book a seat for elio movie at 13:30"

Agent: "To process your booking, I need your full name and email address. 
        Additionally, could you please provide the specific cinema?"

User: "mouad - mzeghraoui@gmail.com - +32494566032 - cinema UGC Ciné Cité Les Halles"

Agent: "I'm sorry, but the showtime at 13:30 is unavailable. However, here are 
        the available showtimes for 'Elio' at UGC Ciné Cité Les Halles:
        - 13:15
        - 15:30  
        - 17:45
        - 20:00
        - 22:10
        Would you like to book a seat for one of these showtimes instead?"

User: "13:15"

Agent: "Booking confirmed for 1 seat for the movie 'Elio' at 13:15.
        - Confirmation ID: BK-7A95180A
        - Customer: Mouad Mzeghraoui
        - Seats: 1 seat(s) in row A
        - Total Cost: €13.50
        - Confirmation Email: Sent to mzeghraoui@gmail.com"
```

**Key Success Indicators:**
- Agent collects required customer information
- Validates showtime availability against actual data
- Provides alternative showtimes when requested time unavailable
- Generates professional booking confirmation with ID and pricing
- Confirms email delivery of booking details

---

## Part 6: Advanced Scenarios

### Test Error Handling

Try edge cases:

**Scenario: Non-existent Movie**
> "Show me showtimes for 'Fake Movie Title'"

**Scenario: Different Location**
> "Find cinemas in Lyon"

**Scenario: Booking Flow**
> "Book 2 seats for Jurassic World Rebirth"



## Part 7: Understanding the Architecture

### Data Flow

```
User Query → Agent (LLM) → Tool Selection → API Call → Response Processing → User
```

### Tool Integration Pattern

1. Python Function with `@tool` decorator
2. Type Hints for parameter validation
3. Connection Injection for API credentials
4. Structured Response format

### Agent Decision Making

The agent uses the **react** style:
- **Reason:** Analyzes user request
- **Act:** Selects appropriate tool
- **Observe:** Processes tool response
- **Respond:** Formats answer for user

---

## Part 8: Key Takeaways

### What You've Learned

1. **Tool Development:** How to create watsonx Orchestrate-compatible Python tools
2. **Connection Management:** Securely handling API credentials
3. **Agent Configuration:** Defining behavior and tool usage patterns
4. **Testing Methodology:** Validating agent responses across scenarios

### Best Practices Demonstrated

1. **Focused Tool Usage:** Each tool has a specific purpose
2. **Clear Instructions:** Agent knows when to use which tool
3. **Error Handling:** Graceful failure modes
4. **User Experience:** Natural conversation flow

### Real-World Applications

This pattern applies to many domains:
- **Customer Service:** FAQ bots with knowledge bases
- **E-commerce:** Product search and ordering
- **Travel:** Flight/hotel booking assistants
- **Finance:** Account management and transactions

---

## Lab Summary

Congratulations! You've successfully:

- ✅ Imported 11 Python tools into watsonx Orchestrate
- ✅ Configured API connections for external services
- ✅ Deployed an intelligent agent with proper tool usage
- ✅ Tested real-world scenarios for movie discovery and booking
- ✅ Understood the architecture of agent-tool integration

You now have a complete foundation for building production-ready AI agents with watsonx Orchestrate!

