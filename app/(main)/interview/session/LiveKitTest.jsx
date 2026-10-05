"use client";

import { useEffect, useId, useMemo } from "react";

import {
  SessionProvider,
  RoomAudioRenderer,
  StartAudio,
  useAgent,
  useSession,
} from "@livekit/components-react";

import { TokenSource } from "livekit-client";

import "@livekit/components-styles";

const tokenServerId =
  process.env.NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID;

const tokenSource = tokenServerId
  ? TokenSource.developmentTokenServer(tokenServerId)
  : null;

function JabariConnection() {
  const agent = useAgent();

  const state = agent.state || "connecting";

  const isFailed = state === "failed";

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
          {state === "connecting"
            ? "Connecting to Jabari..."
            : state === "initializing"
              ? "Jabari is preparing..."
              : state === "listening"
                ? "Listening..."
                : state === "thinking"
                  ? "Thinking..."
                  : state === "speaking"
                    ? "Speaking..."
                    : state === "disconnected"
                      ? "Session ended"
                      : state === "failed"
                        ? "Jabari encountered an error"
                        : state}
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

export default function LiveKitTest() {
  if (!tokenSource) {
    return (
      <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-700">
        NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID is not configured.
      </div>
    );
  }

  return <JabariSession />;
}

function JabariSession() {
  const id = useId();

  const sessionOptions = useMemo(
    () => ({
      roomName: `coachify-jabari-${id}`,
      agentName: "jabari",
    }),
    [id]
  );

  const session = useSession(tokenSource, sessionOptions);

  useEffect(() => {
    let cancelled = false;

    const startSession = async () => {
      try {
        await session.start();
      } catch (error) {
        if (!cancelled) {
          console.error("JABARI SESSION START FAILED:", error);
        }
      }
    };

    startSession();

    return () => {
      cancelled = true;
      void session.end();
    };
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