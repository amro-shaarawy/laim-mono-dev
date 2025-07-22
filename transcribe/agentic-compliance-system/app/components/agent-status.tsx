"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Activity,
  Bot,
  CheckCircle,
  AlertCircle,
  Clock,
  Database,
  Mic,
  FileText,
  Users,
  Shield,
  Zap,
  Settings,
} from "lucide-react"

interface Agent {
  id: string
  name: string
  role: string
  status: "active" | "idle" | "error" | "offline"
  lastActivity: string
  tasksCompleted: number
  cpuUsage: number
  memoryUsage: number
  icon: any
}

interface AgentStatusProps {
  fullView?: boolean
}

export function AgentStatus({ fullView = false }: AgentStatusProps) {
  const [agents] = useState<Agent[]>([
    {
      id: "1",
      name: "AudioIngestAgent",
      role: "Captures live audio, slices into time chunks",
      status: "active",
      lastActivity: "2 seconds ago",
      tasksCompleted: 1247,
      cpuUsage: 45,
      memoryUsage: 32,
      icon: Mic,
    },
    {
      id: "2",
      name: "TranscriberAgent",
      role: "Converts audio to multilingual text using Whisper-Turbo",
      status: "active",
      lastActivity: "5 seconds ago",
      tasksCompleted: 1198,
      cpuUsage: 78,
      memoryUsage: 64,
      icon: FileText,
    },
    {
      id: "3",
      name: "DiarizationAgent",
      role: "Assigns speaker IDs via pyannote",
      status: "active",
      lastActivity: "3 seconds ago",
      tasksCompleted: 1156,
      cpuUsage: 23,
      memoryUsage: 28,
      icon: Users,
    },
    {
      id: "4",
      name: "ComplianceAgent",
      role: "Matches transcript to embedded regulation documents",
      status: "active",
      lastActivity: "1 second ago",
      tasksCompleted: 892,
      cpuUsage: 56,
      memoryUsage: 41,
      icon: Shield,
    },
    {
      id: "5",
      name: "AlertAgent",
      role: "Formats and emits popup alert messages",
      status: "idle",
      lastActivity: "2 minutes ago",
      tasksCompleted: 23,
      cpuUsage: 12,
      memoryUsage: 15,
      icon: AlertCircle,
    },
    {
      id: "6",
      name: "ClassifierAgent",
      role: "Tags new documents with categories before embedding",
      status: "active",
      lastActivity: "30 seconds ago",
      tasksCompleted: 142,
      cpuUsage: 34,
      memoryUsage: 22,
      icon: Bot,
    },
    {
      id: "7",
      name: "EmbedderAgent",
      role: "Embeds documents into vector form and uploads to Pinecone",
      status: "active",
      lastActivity: "45 seconds ago",
      tasksCompleted: 156,
      cpuUsage: 67,
      memoryUsage: 55,
      icon: Database,
    },
    {
      id: "8",
      name: "FrontendBridgeAgent",
      role: "Connects backend agents with frontend for live updates",
      status: "error",
      lastActivity: "5 minutes ago",
      tasksCompleted: 2341,
      cpuUsage: 8,
      memoryUsage: 12,
      icon: Zap,
    },
  ])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case "idle":
        return <Clock className="w-4 h-4 text-yellow-500" />
      case "error":
        return <AlertCircle className="w-4 h-4 text-red-500" />
      case "offline":
        return <AlertCircle className="w-4 h-4 text-gray-500" />
      default:
        return <CheckCircle className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <Badge variant="default" className="bg-green-500">
            Active
          </Badge>
        )
      case "idle":
        return <Badge variant="secondary">Idle</Badge>
      case "error":
        return <Badge variant="destructive">Error</Badge>
      case "offline":
        return <Badge variant="outline">Offline</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const activeAgents = agents.filter((agent) => agent.status === "active").length
  const height = fullView ? "h-[600px]" : "h-[400px]"

  return (
    <Card className={fullView ? "col-span-full" : ""}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Bot className="w-5 h-5" />
              CrewAI Agents
            </CardTitle>
            <CardDescription>Agent orchestration and health monitoring</CardDescription>
          </div>
          <Badge variant="outline">
            {activeAgents}/{agents.length} Active
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className={height}>
          <div className="space-y-4">
            {agents.map((agent) => {
              const IconComponent = agent.icon
              return (
                <Card key={agent.id} className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-slate-100 rounded-lg">
                        <IconComponent className="w-5 h-5 text-slate-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-sm">{agent.name}</h4>
                        <p className="text-xs text-slate-600 max-w-md">{agent.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(agent.status)}
                      {getStatusBadge(agent.status)}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                    <div>
                      <p className="text-slate-500 mb-1">Last Activity</p>
                      <p className="font-medium">{agent.lastActivity}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">Tasks Completed</p>
                      <p className="font-medium">{agent.tasksCompleted.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">CPU Usage</p>
                      <div className="flex items-center gap-2">
                        <Progress value={agent.cpuUsage} className="flex-1 h-2" />
                        <span className="font-medium">{agent.cpuUsage}%</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-slate-500 mb-1">Memory Usage</p>
                      <div className="flex items-center gap-2">
                        <Progress value={agent.memoryUsage} className="flex-1 h-2" />
                        <span className="font-medium">{agent.memoryUsage}%</span>
                      </div>
                    </div>
                  </div>

                  {fullView && (
                    <div className="flex gap-2 mt-3">
                      <Button size="sm" variant="outline">
                        <Settings className="w-3 h-3 mr-1" />
                        Configure
                      </Button>
                      <Button size="sm" variant="outline">
                        <Activity className="w-3 h-3 mr-1" />
                        View Logs
                      </Button>
                    </div>
                  )}
                </Card>
              )
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
