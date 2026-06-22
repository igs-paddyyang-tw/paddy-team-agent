"use client";
import { useEffect, useState } from "react";

interface WsEvent {
  type: string;
  data: Record<string, unknown>;
  source: string;
  timestamp: string;
}

export function useEventStream() {
  const [events, setEvents] = useState<WsEvent[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const host = typeof window !== "undefined" ? window.location.hostname : "localhost";
    const url = `ws://${host}:33333/api/ws/events`;
    let ws: WebSocket;
    let timer: ReturnType<typeof setTimeout>;

    function connect() {
      ws = new WebSocket(url);
      ws.onopen = () => setConnected(true);
      ws.onclose = () => { setConnected(false); timer = setTimeout(connect, 3000); };
      ws.onmessage = (msg) => {
        const event = JSON.parse(msg.data) as WsEvent;
        setEvents((prev) => [event, ...prev].slice(0, 50));
      };
    }
    connect();
    return () => { ws?.close(); clearTimeout(timer); };
  }, []);

  return { events, connected };
}
