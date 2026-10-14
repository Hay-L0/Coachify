import { auth } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";
import { AccessToken } from "livekit-server-sdk";
import { RoomConfiguration } from "@livekit/protocol";

export const runtime = "nodejs";

export async function POST(request) {
  try {
    // Require a signed-in Coachify user.
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json(
        { error: "You must be signed in to start an interview." },
        { status: 401 }
      );
    }

    const body = await request.json();

    const roomName = body.room_name;

    if (
      typeof roomName !== "string" ||
      !/^coachify-jabari-[a-zA-Z0-9_-]{1,150}$/.test(roomName)
    ) {
      return NextResponse.json(
        { error: "Invalid interview room name." },
        { status: 400 }
      );
    }

    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;
    const serverUrl = process.env.LIVEKIT_URL;

    if (!apiKey || !apiSecret || !serverUrl) {
      console.error("Missing required LiveKit server environment variables.");

      return NextResponse.json(
        { error: "LiveKit server configuration is incomplete." },
        { status: 500 }
      );
    }

    const token = new AccessToken(apiKey, apiSecret, {
      identity: `coachify-${userId}`,
      name: body.participant_name || "Candidate",
      ttl: "10m",
    });

    token.addGrant({
      roomJoin: true,
      room: roomName,
      canPublish: true,
      canSubscribe: true,
      canPublishData: true,
    });

    // Preserve the agent dispatch information supplied by LiveKit's
    // TokenSource so the Jabari agent can be dispatched into this room.
    if (body.room_config) {
      token.roomConfig = new RoomConfiguration(body.room_config);
    }

    const participantToken = await token.toJwt();

    return NextResponse.json(
      {
        server_url: serverUrl,
        participant_token: participantToken,
      },
      { status: 201 }
    );
  } catch (error) {
    console.error("LIVEKIT TOKEN ERROR:", error);

    return NextResponse.json(
      { error: "Unable to create the LiveKit connection token." },
      { status: 500 }
    );
  }
}