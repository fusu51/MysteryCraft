import { createContext, useContext, useReducer, type Dispatch } from "react";
import type { AppState, MonitorEvent, FileItem, SessionRecord, ConnectionStatus } from "../types";

// ====== Actions ======
type Action =
    | { type: "SET_THREAD"; threadId: string }
    | { type: "SET_SESSION_DIR"; dir: string }
    | { type: "SET_CONNECTION_STATUS"; status: ConnectionStatus }
    | { type: "ADD_EVENT"; event: MonitorEvent }
    | { type: "CLEAR_EVENTS" }
    | { type: "SET_LOADING"; isLoading: boolean }
    | { type: "SET_FILES"; files: FileItem[] }
    | { type: "ADD_SESSION"; session: SessionRecord }
    | { type: "SET_SESSIONS"; sessions: SessionRecord[] }
    | { type: "SET_ACTIVE_SESSION"; threadId: string | null }
    | { type: "RESET_PANEL" };

// ====== Initial State ======
const initialState: AppState = {
    threadId: null,
    sessionDir: null,
    connectionStatus: "disconnected",
    events: [],
    isLoading: false,
    files: [],
    sessions: [],
    activeSession: null,
};

// ====== Reducer ======
function reducer(state: AppState, action: Action): AppState {
    switch (action.type) {
        case "SET_THREAD":
            return { ...state, threadId: action.threadId };
        case "SET_SESSION_DIR":
            return { ...state, sessionDir: action.dir };
        case "SET_CONNECTION_STATUS":
            return { ...state, connectionStatus: action.status };
        case "ADD_EVENT":
            return { ...state, events: [...state.events, action.event] };
        case "CLEAR_EVENTS":
            return { ...state, events: [] };
        case "SET_LOADING":
            return { ...state, isLoading: action.isLoading };
        case "SET_FILES":
            return { ...state, files: action.files };
        case "ADD_SESSION":
            return {
                ...state,
                sessions: [action.session, ...state.sessions.filter(s => s.thread_id !== action.session.thread_id)],
            };
        case "SET_SESSIONS":
            return { ...state, sessions: action.sessions };
        case "SET_ACTIVE_SESSION":
            return { ...state, activeSession: action.threadId };
        case "RESET_PANEL":
            return { ...state, events: [], files: [], threadId: null, sessionDir: null, isLoading: false, connectionStatus: "disconnected" };
        default:
            return state;
    }
}

// ====== Context ======
const AppCtx = createContext<AppState>(initialState);
const DispatchCtx = createContext<Dispatch<Action>>(() => {});

export function AppProvider({ children }: { children: React.ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    return (
        <AppCtx.Provider value={state}>
            <DispatchCtx.Provider value={dispatch}>
                {children}
            </DispatchCtx.Provider>
        </AppCtx.Provider>
    );
}

export function useAppState() {
    return useContext(AppCtx);
}

export function useDispatch() {
    return useContext(DispatchCtx);
}
