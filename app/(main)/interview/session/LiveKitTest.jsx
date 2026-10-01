"use client";

import { useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
} from "@livekit/components-react";
import { TokenSource } from "livekit-client";

import "@livekit/components-styles";

export default function LiveKitTest() {
  const [connection, setConnection] = useState(null);
  const [error, setError] = useState("");

  async function connectToLiveKit() {
    try {
      setError("");

      const tokenServerId =
        process.env.NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID;

      if (!tokenServerId) {
        throw new Error(
          "NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID is not configured."
        );
      }

      const tokenSource =
        TokenSource.developmentTokenServer(
          tokenServerId
        );

      const credentials =
        await tokenSource.fetch({
          roomName: `coachify-test-${Date.now()}`,
        });

      setConnection({
        token: credentials.participantToken,
        serverUrl: credentials.serverUrl,
      });
    } catch (err) {
      console.error(
        "LIVEKIT CONNECTION ERROR:",
        err
      );

      setError(
        err instanceof Error
          ? err.message
          : "Failed to connect to LiveKit."
      );
    }
  }

  if (!connection) {
    return (
      <div className="flex flex-col items-center gap-4 rounded-2xl border p-8">
        <div className="flex h-32 w-32 items-center justify-center rounded-full bg-black">
          <div className="h-20 w-20 rounded-full bg-white/20" />
        </div>

        <h2 className="text-xl font-semibold">
          Jabari
        </h2>

        <p className="text-sm text-muted-foreground">
          LiveKit connection test
        </p>

        <button
          type="button"
          onClick={connectToLiveKit}
          className="rounded-lg bg-black px-5 py-2 text-white"
        >
          Connect to LiveKit
        </button>

        {error && (
          <p className="max-w-md text-center text-sm text-red-500">
            {error}
          </p>
        )}
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={connection.token}
      serverUrl={connection.serverUrl}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={() => {
        setConnection(null);
      }}
    >
      <div className="flex flex-col items-center gap-4 rounded-2xl border p-8">
        <div className="flex h-32 w-32 items-center justify-center rounded-full bg-black">
          <div className="h-20 w-20 animate-pulse rounded-full bg-white/30" />
        </div>

        <h2 className="text-xl font-semibold">
          Jabari
        </h2>

        <p className="text-sm text-green-600">
          Connected to LiveKit
        </p>
      </div>

      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}