"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { User, Clock, Mic } from "lucide-react"

interface TranscriptEntry {
  id: string
  speaker: string
  text: string
  timestamp: string
  confidence: number
  flagged?: boolean
}

interface LiveTranscriptionProps {
  isRecording: boolean
  fullView?: boolean
}

export function LiveTranscription({ isRecording, fullView = false }: LiveTranscriptionProps) {
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([
    {
      id: "1",
      speaker: "Speaker 1",
      text: "Good morning everyone, let's begin today's board meeting.",
      timestamp: "09:00:12",
      confidence: 0.95,
    },
    {
      id: "2",
      speaker: "Speaker 2",
      text: "Thank you. I'd like to discuss our Q3 financial results and some regulatory updates.",
      timestamp: "09:00:28",
      confidence: 0.92,
    },
    {
      id: "3",
      speaker: "Speaker 1",
      text: "Before we proceed, I should mention that we have some insider information about the upcoming merger.",
      timestamp: "09:01:15",
      confidence: 0.88,
      flagged: true,
    },
  ])

  const [currentSpeaker, setCurrentSpeaker] = useState<string>("")

  useEffect(() => {
    if (!isRecording) return

    const interval = setInterval(
      () => {
        const speakers = ["Speaker 1", "Speaker 2", "Speaker 3"]
        const sampleTexts = [
          "We need to ensure compliance with all regulatory requirements.",
          "The new GDPR guidelines require additional data protection measures.",
          "Our anti-trust policies must be strictly followed.",
          "I have some confidential information about our competitor's strategy.",
          "We should discuss the potential conflicts of interest.",
          "The board needs to approve these financial disclosures.",
        ]

        const newEntry: TranscriptEntry = {
          id: Date.now().toString(),
          speaker: speakers[Math.floor(Math.random() * speakers.length)],
          text: sampleTexts[Math.floor(Math.random() * sampleTexts.length)],
          timestamp: new Date().toLocaleTimeString(),
          confidence: 0.85 + Math.random() * 0.15,
          flagged: Math.random() > 0.8,
        }

        setTranscript((prev) => [...prev.slice(-20), newEntry])
        setCurrentSpeaker(newEntry.speaker)
      },
      3000 + Math.random() * 2000,
    )

    return () => clearInterval(interval)
  }, [isRecording])

  const height = fullView ? "h-[600px]" : "h-[400px]"

  return (
    <Card className={fullView ? "col-span-full" : ""}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Mic className="w-5 h-5" />
              Live Transcription
            </CardTitle>
            <CardDescription>Real-time speech-to-text with speaker diarization</CardDescription>
          </div>
          {isRecording && (
            <Badge variant="default" className="animate-pulse">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-2" />
              Recording
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className={height}>
          <div className="space-y-4">
            {transcript.map((entry, index) => (
              <div key={entry.id}>
                <div className={`p-3 rounded-lg ${entry.flagged ? "bg-red-50 border border-red-200" : "bg-slate-50"}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-slate-500" />
                      <span className="font-medium text-sm">{entry.speaker}</span>
                      {entry.flagged && (
                        <Badge variant="destructive" size="sm">
                          Flagged
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <Clock className="w-3 h-3" />
                      {entry.timestamp}
                      <span>({Math.round(entry.confidence * 100)}%)</span>
                    </div>
                  </div>
                  <p className="text-sm leading-relaxed">{entry.text}</p>
                </div>
                {index < transcript.length - 1 && <Separator className="my-2" />}
              </div>
            ))}

            {isRecording && currentSpeaker && (
              <div className="p-3 rounded-lg bg-blue-50 border border-blue-200 animate-pulse">
                <div className="flex items-center gap-2 mb-2">
                  <User className="w-4 h-4 text-blue-500" />
                  <span className="font-medium text-sm">{currentSpeaker}</span>
                  <Badge variant="outline" size="sm">
                    Speaking...
                  </Badge>
                </div>
                <p className="text-sm text-slate-600 italic">Transcribing audio...</p>
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
