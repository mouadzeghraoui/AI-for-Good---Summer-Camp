# Augmenting Your Agent with External Knowledge - RAG System

In this section we will augment our Agent with external knowledge using a RAG (Retrieval Augmented Generation) system. We will include knowledge for Marvel and MCU universe.

## Step 1: Add Knowledge Description

We need to include a description of the knowledge that we want to add.

![capture 2025-07-07 at 18.14.41@2x](/Users/mouad/Library/Application Support/CleanShot/media/media_2GYP0LhYlR/capture 2025-07-07 at 18.14.41@2x.png)

### Example

```
## KNOWLEDGE DOMAIN: MARVEL CINEMATIC UNIVERSE (MCU)  
**Content Type**: Fun, educational trivia for high school students  
**Key Topics Covered**:  

1. **CHARACTER PROFILES**  
   - Powers, weaknesses, real names  
   - Psychological motivations  
   - Behind-the-scenes actor trivia  
   - *Heroes*: Iron Man, Spider-Man, Black Panther, Thor, Captain Marvel, etc.  
   - *Villains*: Thanos, Loki, Killmonger, Ultron  

2. **SCIENCE & TECHNOLOGY**  
   - Vibranium properties vs. real-world parallels (graphene, piezoelectricity)  
   - Wakandan tech (kimoyo beads, energy shields)  
   - Quantum realm/multiverse "rules"  
   - Suit engineering (Iron Man, Spider-Man)  

3. **TIMELINE & EVENTS**  
   - Phase 1-5 chronology (2008-present)  
   - Major battles (Battle of NYC, Endgame finale)  
   - The Blip/Snap mechanics  
   - Time travel logic in *Endgame*  

4. **POP CULTURE ANALYSIS**  
   - "Who Would Win?" matchups (Hulk vs. Thor, Wanda vs. Strange)  
   - Ethical debates (Thanos' plan, Superhero Registration Act)  
   - Easter eggs & hidden references  
   - Real-world STEM connections  

5. **BEHIND-THE-SCENES**  
   - Improvised lines (e.g., "I am Iron Man")  
   - Actor audition stories  
   - Deleted scene lore  
   - CGI vs. practical effects  
```

The agent will automatically understand when to use this external knowledge based on the provided description.

## Step 2: Upload Documents

Second, we need to upload the documents - such as .docx, .pdf, .pptx and .xlsx etc.

![capture 2025-07-07 at 18.16.36@2x](/Users/mouad/Library/Application Support/CleanShot/media/media_gEGJPrnZBg/capture 2025-07-07 at 18.16.36@2x.png)

PS: For more advanced users, we can include a Vector DB as content repository instead of uploading files manually.

![capture 2025-07-07 at 18.18.20@2x](/Users/mouad/Library/Application Support/CleanShot/media/media_Dp5OzL0Uku/capture 2025-07-07 at 18.18.20@2x.png)