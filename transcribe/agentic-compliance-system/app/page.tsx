"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Mic, MicOff, FileText, AlertTriangle, Activity, Pause, Volume2 } from "lucide-react"
import { LiveTranscription } from "./components/live-transcription"
import { DocumentManager } from "./components/document-manager"
import { ComplianceAlerts } from "./components/compliance-alerts"
import { AgentStatus } from "./components/agent-status"

interface SystemStats {
  isRecording: boolean
  activeAgents: number
  totalAgents: number
  documentsProcessed: number
  alertsToday: number
  uptime: string
}

export default function ComplianceDashboard() {
  const [activeTab, setActiveTab] = useState("dashboard")
  const [isRecording, setIsRecording] = useState(false)
  const [systemStats, setSystemStats] = useState<SystemStats>({
    isRecording: false,
    activeAgents: 7,
    totalAgents: 8,
    documentsProcessed: 142,
    alertsToday: 3,
    uptime: "2h 34m",
  })

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    setSystemStats((prev) => ({ ...prev, isRecording: !prev.isRecording }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">🧱 Agentic AI Compliance System</h1>
            <p className="text-slate-600 mt-1">Real-time compliance monitoring with AI agents</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant={isRecording ? "default" : "secondary"} className="px-3 py-1">
              {isRecording ? (
                <>
                  <Activity className="w-4 h-4 mr-1 animate-pulse" />
                  Live
                </>
              ) : (
                <>
                  <Pause className="w-4 h-4 mr-1" />
                  Stopped
                </>
              )}
            </Badge>
            <Button onClick={toggleRecording} variant={isRecording ? "destructive" : "default"} size="lg">
              {isRecording ? (
                <>
                  <MicOff className="w-4 h-4 mr-2" />
                  Stop Recording
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4 mr-2" />
                  Start Recording
                </>
              )}
            </Button>
          </div>
        </div>

        {/* System Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {systemStats.activeAgents}/{systemStats.totalAgents}
              </div>
              <Progress value={(systemStats.activeAgents / systemStats.totalAgents) * 100} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Documents Processed</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.documentsProcessed}</div>
              <p className="text-xs text-muted-foreground">+12 from yesterday</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Alerts Today</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{systemStats.alertsToday}</div>
              <p className="text-xs text-muted-foreground">2 high priority</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
              <Volume2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{systemStats.uptime}</div>
              <p className="text-xs text-muted-foreground">99.9% availability</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="transcription">Live Transcription</TabsTrigger>
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="agents">Agents</TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LiveTranscription isRecording={isRecording} />
              <ComplianceAlerts />
            </div>
            <AgentStatus />
          </TabsContent>

          <TabsContent value="transcription">
            <LiveTranscription isRecording={isRecording} fullView />
          </TabsContent>

          <TabsContent value="documents">
            <DocumentManager />
          </TabsContent>

          <TabsContent value="alerts">
            <ComplianceAlerts fullView />
          </TabsContent>

          <TabsContent value="agents">
            <AgentStatus fullView />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
