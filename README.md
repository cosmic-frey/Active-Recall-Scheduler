# Active-Recall-Scheduler
This is a side project where I made an active recall scheduler for my Biochemistry, M1 and M2 (Development) modules for term 1 of my final year at University. I then began experimenting with interactive UI in Python, because I'm picky and wanted it to look nicer. 
(This brought me so much joy)  
# Basic Rules:  
- Modules are the lists and the topics within them are the list components
    - The length of module lists were altered prior to creating the scheduler
- A week is defined as 8 days (monday - monday) 
- Topics within modules could only be repeated a minimum of two days apart (middle day skipped)
  - Therefore topics cannot be repeated within the same day or on consecutive days
- M1 and Development topics needed to be covered twice per week
- Biochem topics needed to be covered three times per week (with the exception of Chromatin)
  - Chromatin needed to be scheduled on the same days as the Rosana+Antoine topic in M1 (as the material was similar)
    - Because of this Chromatin rule, Chromatin only needed to be repeated twice per week
- Due to basic maths:
  - 2 Development topics must be scheduled each day
  - 2-3 Biochem topics must be scheduled each day
  - 1 M1 topic must be scheduled each day
  - (Is this sustainable? I'll find out)
- There must be an option to include a shuffle function (because as a human I want the illusion of choice)

# Feature Requirements:
- The final output I wanted was a (cute) visual image of a calendar
  - I also wanted this calendar to automatically open on my laptop, but also make the auto-pop-up section of code easy to see so that it could be removed
  - I also wanted the option to auto-update the calendar when I created the shuffle feature
   
# Extension Ideas:
- An interactive UI
- An interactive shuffle button
- A shortcut to change rules within the UI
- A shortcut to change modules/topics or add them within the UI (instead of directly changing the code)

# Extension-Extension Ideas:
- Could the calendar integrate with outlook/goodle calendars and auto-update within them?
- Could the calendar be auto-saved to a notes app/ sticky notes app? (and also auto-update?)
- Could the calendar be added as a shortcut feature on the taskbar?


