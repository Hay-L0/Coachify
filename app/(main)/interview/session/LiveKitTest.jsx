"use client";

import { useEffect, useMemo } from "react";

import {
  SessionProvider,
  RoomAudioRenderer,
  StartAudio,
  useAgent,
  useSession,
} from "@livekit/components-react";

import { TokenSource } from "livekit-client";
import "@livekit/components-styles";

const tokenSource = TokenSource.endpoint("/api/livekit/token");

function JabariConnection() {
  const agent = useAgent();
  const state = agent.state || "connecting";
  const isFailed = state === "failed";

  const statusText = {
    connecting: "Connecting to Jabari...",
    initializing: "Jabari is preparing...",
    listening: "Listening...",
    thinking: "Thinking...",
    speaking: "Speaking...",
    disconnected: "Session ended",
    failed: "Jabari encountered an error",
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        className={`flex h-32 w-32 items-center justify-center rounded-full border-2 shadow-xl transition-all duration-500 ${
          state === "speaking"
            ? "border-blue-400 shadow-blue-500/40"
            : state === "listening"
              ? "border-green-400"
              : isFailed
                ? "border-red-400"
                : "border-white/20"
        }`}
      >
        <div className="h-20 w-20 rounded-full bg-white/10" />
      </div>

      <div className="text-center">
        <p className="font-semibold">Jabari</p>

        <p className="text-sm text-muted-foreground">
          {statusText[state] || state}
        </p>

        {isFailed && agent.failureReasons?.length > 0 && (
          <p className="mt-2 text-xs text-red-500">
            {agent.failureReasons.join(", ")}
          </p>
        )}
      </div>

      <StartAudio label="Enable Jabari Audio" />
    </div>
  );
}

export default function LiveKitTest({ sessionId }) {
  if (!sessionId) {
    return (
      <div className="rounded-xl border p-4 text-sm">
        Interview session ID is missing.
      </div>
    );
  }

  return <JabariSession sessionId={sessionId} />;
}

function JabariSession({ sessionId }) {
  const sessionOptions = useMemo(
    () => ({
      roomName: `coachify-jabari-${sessionId}`,
      agentName: "jabari",
    }),
    [sessionId]
  );

  const session = useSession(tokenSource, sessionOptions);

  useEffect(() => {
    let cancelled = false;

    async function startSession() {
      try {
        await session.start();
      } catch (error) {
        if (!cancelled) {
          console.error("JABARI SESSION START FAILED:", error);
        }
      }
    }

    void startSession();

    return () => {
      cancelled = true;
      void session.end();
    };
    // LiveKit's Session API example starts and ends the session
    // once per component mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <SessionProvider session={session}>
      <div className="flex min-h-[250px] items-center justify-center">
        <JabariConnection />
      </div>

      <RoomAudioRenderer />
    </SessionProvider>
  );
}