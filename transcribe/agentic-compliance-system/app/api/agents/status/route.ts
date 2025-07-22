import { NextResponse } from "next/server"

export async function GET() {
  // Mock agent status data
  const agents = [
    {
      id: "audio-ingest",
      name: "AudioIngestAgent",
      status: "active",
      lastActivity: new Date().toISOString(),
      tasksCompleted: Math.floor(Math.random() * 1000) + 1000,
      cpuUsage: Math.floor(Math.random() * 50) + 20,
      memoryUsage: Math.floor(Math.random() * 40) + 20,
    },
    {
      id: "transcriber",
      name: "TranscriberAgent",
      status: "active",
      lastActivity: new Date().toISOString(),
      tasksCompleted: Math.floor(Math.random() * 1000) + 800,
      cpuUsage: Math.floor(Math.random() * 60) + 40,
      memoryUsage: Math.floor(Math.random() * 50) + 30,
    },
    // Add more agents as needed
  ]

  return NextResponse.json({ agents })
}
