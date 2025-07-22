import { NextResponse } from "next/server"

export async function GET() {
  // Mock live transcription data
  const transcriptEntry = {
    id: Date.now().toString(),
    speaker: `Speaker ${Math.floor(Math.random() * 3) + 1}`,
    text: [
      "We need to ensure compliance with all regulatory requirements.",
      "The new GDPR guidelines require additional data protection measures.",
      "Our anti-trust policies must be strictly followed.",
      "I have some confidential information about our competitor's strategy.",
      "We should discuss the potential conflicts of interest.",
      "The board needs to approve these financial disclosures.",
    ][Math.floor(Math.random() * 6)],
    timestamp: new Date().toLocaleTimeString(),
    confidence: 0.85 + Math.random() * 0.15,
    flagged: Math.random() > 0.8,
  }

  return NextResponse.json({ transcript: transcriptEntry })
}
