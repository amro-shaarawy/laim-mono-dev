import { NextResponse } from "next/server"

export async function GET() {
  // Mock compliance alerts
  const alerts = [
    {
      id: Date.now().toString(),
      type: "high",
      title: "Potential Insider Trading Violation",
      description: "Discussion of non-public material information detected",
      speaker: "Speaker 1",
      timestamp: new Date().toLocaleTimeString(),
      regulation: "SEC Rule 10b-5",
      similarity: 0.92,
      transcript: "I should mention that we have some insider information about the upcoming merger.",
    },
  ]

  return NextResponse.json({ alerts })
}

export async function POST(request: Request) {
  const { alertId, action } = await request.json()

  // Mock alert action handling
  return NextResponse.json({
    success: true,
    message: `Alert ${alertId} ${action}ed successfully`,
  })
}
