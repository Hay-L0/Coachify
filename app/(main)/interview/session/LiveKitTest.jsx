"use client";

import { useEffect } from "react";
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

function JabariConnection() {
  const agent = useAgent();

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex h-32 w-32 items-center justify-center rounded-full border-2 border-white/20 bg-black shadow-xl">
        <div className="h-20 w-20 rounded-full bg-white/10" />
      </div>

      <div className="text-center">
        <p className="font-semibold">Jabari</p>

        <p className="text-sm text-muted-foreground">
          {agent.state || "Connecting..."}
        </p>
      </div>

      <StartAudio label="Enable Jabari Audio" />
    </div>
  );
}

export default function LiveKitTest() {
  if (!tokenServerId) {
    return (
      <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-700">
        NEXT_PUBLIC_LIVEKIT_TOKEN_SERVER_ID is not configured.
      </div>
    );
  }

  return <JabariSession />;
}

function JabariSession() {
  const tokenSource =
    TokenSource.developmentTokenServer(tokenServerId);

  const session = useSession(tokenSource, {
    roomName: `coachify-test-${Date.now()}`,
    agentName: "jabari",
  });

  useEffect(() => {
    console.log("JABARI: starting LiveKit session");

    session.start();

    return () => {
      console.log("JABARI: ending LiveKit session");
      session.end();
    };
  }, [session]);

  return (
    <SessionProvider session={session}>
      <div className="flex min-h-[250px] items-center justify-center">
        <JabariConnection />
      </div>

      <RoomAudioRenderer />
    </SessionProvider>
  );
}