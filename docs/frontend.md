# Frontend Documentation

The frontend is designed to be a sleek, high-performance interface with a premium aesthetic. It leverages modern React paradigms to consume streaming data from the backend dynamically.

## 1. Core Architecture & Styling

- **Framework:** React 18+ bootstrapped with Vite (`react-ts` template).
- **Styling Engine:** Tailwind CSS with a custom configuration.
- **Theme:** Deep space Dark Mode. Key colors include Slate (`#1E293B`), Indigo (`#6366F1`), and vibrant Purple (`#A855F7`).
- **Glassmorphism:** A centralized `.glass` utility class handles backdrop blurs, slight opacity, and white borders to give components a translucent floating appearance.
- **Markdown Rendering:** `react-markdown` coupled with `@tailwindcss/typography` (`prose prose-invert`) to style the final LLM-generated report safely.

---

## 2. Component Structure

### `App.tsx`
The root layout manager. It holds the global state for user limitations, specifically tracking `sessionCredits`. It controls the visibility of the BYOK Modal and houses the global Header and Credit HUD.

### `ResearchUI.tsx`
The core interactable component containing the user input field, the live terminal HUD, and the report renderer.
- **SSE Consumer Logic:** 
  It utilizes the native browser `EventSource` API to open a connection to the backend stream endpoint (`/api/stream/{topic}`). 
- **Event Listeners:** 
  Listens for the `update` event to append new JSON logs to the terminal view, auto-scrolling utilizing a `useRef` tied to the bottom of the log container. Upon receiving the `synthesizer` payload containing the `report` property, it triggers the final render.

### `BYOKModal.tsx` (Bring Your Own Key)
A gatekeeping UI component built to prevent API abuse.
- **Trigger:** Appears dynamically when the user hits `0` free session credits.
- **Functionality:** Disables background interaction (`z-50`, backdrop blur overlay) and prompts the user to select an LLM provider (Groq or Google Gemini) and input their personal API key. 
- **Execution:** Once submitted, the key and provider are lifted to the `App` state and passed down as an override to all subsequent `/api/research` requests.

### `MarkdownReport.tsx`
A wrapper around `ReactMarkdown` that handles the beautiful formatting of the deeply cited final response from the Synthesizer node. Utilizing the `animate-in` utilities, it smoothly slides into view once the graph concludes its cycle.

---

## 3. Communication Flow

1. User enters a topic and presses **Start**.
2. A `POST` request goes to `/api/research` with an attached `session_id`. The backend approves the session and deducts a credit.
3. The frontend immediately opens an `EventSource` stream.
4. The React state updates the terminal log (`setLogs`) live as LangGraph pushes node states to the stream.
5. The connection is naturally terminated (`eventSource.close()`) when the backend fires the `done` event.
