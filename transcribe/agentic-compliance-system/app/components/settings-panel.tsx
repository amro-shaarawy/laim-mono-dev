"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Settings, Save } from "lucide-react"

export function SettingsPanel() {
  const [settings, setSettings] = useState({
    pineconeApiKey: "••••••••••••••••",
    pineconeIndex: "compliance-docs",
    whisperModel: "whisper-turbo-v3",
    similarityThreshold: [0.85],
    enableRealTimeAlerts: true,
    enableAudioRecording: true,
    maxSpeakers: 5,
    chunkSize: 10,
    alertSeverity: "medium",
  })

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            System Configuration
          </CardTitle>
          <CardDescription>Configure AI agents and system parameters</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="general" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="audio">Audio</TabsTrigger>
              <TabsTrigger value="compliance">Compliance</TabsTrigger>
              <TabsTrigger value="alerts">Alerts</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="pinecone-key">Pinecone API Key</Label>
                    <Input
                      id="pinecone-key"
                      type="password"
                      value={settings.pineconeApiKey}
                      onChange={(e) => setSettings((prev) => ({ ...prev, pineconeApiKey: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="pinecone-index">Pinecone Index</Label>
                    <Input
                      id="pinecone-index"
                      value={settings.pineconeIndex}
                      onChange={(e) => setSettings((prev) => ({ ...prev, pineconeIndex: e.target.value }))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="whisper-model">Whisper Model</Label>
                  <select
                    id="whisper-model"
                    value={settings.whisperModel}
                    onChange={(e) => setSettings((prev) => ({ ...prev, whisperModel: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md"
                  >
                    <option value="whisper-turbo-v3">Whisper Turbo v3</option>
                    <option value="whisper-large-v2">Whisper Large v2</option>
                    <option value="whisper-medium">Whisper Medium</option>
                  </select>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="audio" className="space-y-4">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Enable Audio Recording</Label>
                    <p className="text-sm text-slate-500">Allow system to capture live audio</p>
                  </div>
                  <Switch
                    checked={settings.enableAudioRecording}
                    onCheckedChange={(checked) => setSettings((prev) => ({ ...prev, enableAudioRecording: checked }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Maximum Speakers: {settings.maxSpeakers}</Label>
                  <Slider
                    value={[settings.maxSpeakers]}
                    onValueChange={(value) => setSettings((prev) => ({ ...prev, maxSpeakers: value[0] }))}
                    max={10}
                    min={2}
                    step={1}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Audio Chunk Size (seconds): {settings.chunkSize}</Label>
                  <Slider
                    value={[settings.chunkSize]}
                    onValueChange={(value) => setSettings((prev) => ({ ...prev, chunkSize: value[0] }))}
                    max={30}
                    min={5}
                    step={5}
                    className="w-full"
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="compliance" className="space-y-4">
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label>Similarity Threshold: {settings.similarityThreshold[0]}</Label>
                  <p className="text-sm text-slate-500">Minimum similarity score to trigger alerts</p>
                  <Slider
                    value={settings.similarityThreshold}
                    onValueChange={(value) => setSettings((prev) => ({ ...prev, similarityThreshold: value }))}
                    max={1}
                    min={0.5}
                    step={0.05}
                    className="w-full"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Alert Severity Level</Label>
                  <select
                    value={settings.alertSeverity}
                    onChange={(e) => setSettings((prev) => ({ ...prev, alertSeverity: e.target.value }))}
                    className="w-full px-3 py-2 border border-slate-300 rounded-md"
                  >
                    <option value="low">Low - All potential violations</option>
                    <option value="medium">Medium - Moderate confidence violations</option>
                    <option value="high">High - Only high confidence violations</option>
                  </select>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="alerts" className="space-y-4">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Real-time Alerts</Label>
                    <p className="text-sm text-slate-500">Show popup alerts during live monitoring</p>
                  </div>
                  <Switch
                    checked={settings.enableRealTimeAlerts}
                    onCheckedChange={(checked) => setSettings((prev) => ({ ...prev, enableRealTimeAlerts: checked }))}
                  />
                </div>

                <div className="p-4 bg-slate-50 rounded-lg">
                  <h4 className="font-medium mb-2">Alert Categories</h4>
                  <div className="space-y-2">
                    {["GDPR Violations", "Insider Trading", "Anti-trust", "Financial Disclosure"].map((category) => (
                      <div key={category} className="flex items-center justify-between">
                        <Label className="text-sm">{category}</Label>
                        <Switch defaultChecked />
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>

          <div className="flex justify-end pt-6 border-t">
            <Button>
              <Save className="w-4 h-4 mr-2" />
              Save Configuration
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
