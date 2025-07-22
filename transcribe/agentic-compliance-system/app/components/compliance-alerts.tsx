"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertTriangle, Clock, User, FileText, Eye, X, AlertCircle, Shield } from "lucide-react"

interface ComplianceAlert {
  id: string
  type: "high" | "medium" | "low"
  title: string
  description: string
  speaker: string
  timestamp: string
  regulation: string
  similarity: number
  transcript: string
  dismissed?: boolean
}

interface ComplianceAlertsProps {
  fullView?: boolean
}

export function ComplianceAlerts({ fullView = false }: ComplianceAlertsProps) {
  const [alerts, setAlerts] = useState<ComplianceAlert[]>([
    {
      id: "1",
      type: "high",
      title: "Potential Insider Trading Violation",
      description: "Discussion of non-public material information detected",
      speaker: "Speaker 1",
      timestamp: "09:01:15",
      regulation: "SEC Rule 10b-5",
      similarity: 0.92,
      transcript: "I should mention that we have some insider information about the upcoming merger.",
    },
    {
      id: "2",
      type: "medium",
      title: "GDPR Data Processing Concern",
      description: "Potential data handling violation mentioned",
      speaker: "Speaker 2",
      timestamp: "09:05:32",
      regulation: "GDPR Article 6",
      similarity: 0.87,
      transcript: "We can access customer data without explicit consent for this analysis.",
    },
    {
      id: "3",
      type: "low",
      title: "Anti-trust Discussion",
      description: "Competitive behavior discussion flagged",
      speaker: "Speaker 3",
      timestamp: "09:12:45",
      regulation: "Sherman Act Section 1",
      similarity: 0.78,
      transcript: "We should coordinate pricing with our main competitor.",
    },
  ])

  const dismissAlert = (id: string) => {
    setAlerts((prev) => prev.map((alert) => (alert.id === id ? { ...alert, dismissed: true } : alert)))
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "high":
        return <AlertTriangle className="w-4 h-4" />
      case "medium":
        return <AlertCircle className="w-4 h-4" />
      case "low":
        return <Shield className="w-4 h-4" />
      default:
        return <AlertTriangle className="w-4 h-4" />
    }
  }

  const getAlertVariant = (type: string) => {
    switch (type) {
      case "high":
        return "destructive"
      case "medium":
        return "default"
      case "low":
        return "secondary"
      default:
        return "default"
    }
  }

  const activeAlerts = alerts.filter((alert) => !alert.dismissed)
  const height = fullView ? "h-[600px]" : "h-[400px]"

  return (
    <Card className={fullView ? "col-span-full" : ""}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Compliance Alerts
            </CardTitle>
            <CardDescription>Real-time regulatory violation detection</CardDescription>
          </div>
          <Badge variant="outline">{activeAlerts.length} Active</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className={height}>
          <div className="space-y-4">
            {activeAlerts.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Shield className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No active compliance alerts</p>
                <p className="text-sm">System is monitoring for violations</p>
              </div>
            ) : (
              activeAlerts.map((alert) => (
                <Alert key={alert.id} className="relative">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      {getAlertIcon(alert.type)}
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <AlertTitle className="text-sm font-semibold">{alert.title}</AlertTitle>
                          <Badge variant={getAlertVariant(alert.type) as any} size="sm">
                            {alert.type.toUpperCase()}
                          </Badge>
                        </div>
                        <AlertDescription className="text-sm">{alert.description}</AlertDescription>

                        <div className="grid grid-cols-2 gap-4 text-xs text-slate-600">
                          <div className="flex items-center gap-1">
                            <User className="w-3 h-3" />
                            {alert.speaker}
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {alert.timestamp}
                          </div>
                          <div className="flex items-center gap-1">
                            <FileText className="w-3 h-3" />
                            {alert.regulation}
                          </div>
                          <div className="flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" />
                            {Math.round(alert.similarity * 100)}% match
                          </div>
                        </div>

                        <div className="p-2 bg-slate-50 rounded text-xs italic">"{alert.transcript}"</div>

                        <div className="flex gap-2">
                          <Button size="sm" variant="outline">
                            <Eye className="w-3 h-3 mr-1" />
                            View Context
                          </Button>
                          <Button size="sm" variant="ghost" onClick={() => dismissAlert(alert.id)}>
                            <X className="w-3 h-3 mr-1" />
                            Dismiss
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </Alert>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
