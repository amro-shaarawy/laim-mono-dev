"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Upload, FileText, Search, Download, Trash2, Eye, Tag, Calendar, Database } from "lucide-react"

interface Document {
  id: string
  name: string
  category: string
  uploadDate: string
  size: string
  status: "processed" | "processing" | "error"
  embeddings: number
  similarity?: number
}

export function DocumentManager() {
  const [documents] = useState<Document[]>([
    {
      id: "1",
      name: "GDPR Compliance Guidelines.pdf",
      category: "Data Protection",
      uploadDate: "2024-01-15",
      size: "2.4 MB",
      status: "processed",
      embeddings: 1247,
    },
    {
      id: "2",
      name: "SEC Rule 10b-5 Insider Trading.pdf",
      category: "Securities Law",
      uploadDate: "2024-01-14",
      size: "1.8 MB",
      status: "processed",
      embeddings: 892,
    },
    {
      id: "3",
      name: "Sherman Act Anti-trust Guidelines.pdf",
      category: "Anti-trust",
      uploadDate: "2024-01-13",
      size: "3.2 MB",
      status: "processed",
      embeddings: 1456,
    },
    {
      id: "4",
      name: "Corporate Governance Best Practices.pdf",
      category: "Governance",
      uploadDate: "2024-01-12",
      size: "1.5 MB",
      status: "processing",
      embeddings: 0,
    },
    {
      id: "5",
      name: "Financial Disclosure Requirements.pdf",
      category: "Financial",
      uploadDate: "2024-01-11",
      size: "2.1 MB",
      status: "error",
      embeddings: 0,
    },
  ])

  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")

  const categories = ["all", "Data Protection", "Securities Law", "Anti-trust", "Governance", "Financial"]

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || doc.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "processed":
        return (
          <Badge variant="default" className="bg-green-500">
            Processed
          </Badge>
        )
      case "processing":
        return <Badge variant="secondary">Processing</Badge>
      case "error":
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Document Upload
          </CardTitle>
          <CardDescription>Upload regulatory documents for compliance monitoring</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
            <p className="text-lg font-medium mb-2">Drop files here or click to upload</p>
            <p className="text-sm text-slate-500 mb-4">Supports PDF, DOC, DOCX files up to 10MB</p>
            <Button>
              <Upload className="w-4 h-4 mr-2" />
              Choose Files
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Document Library */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Document Library
              </CardTitle>
              <CardDescription>Manage and search regulatory documents</CardDescription>
            </div>
            <Badge variant="outline">{documents.length} Documents</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="library" className="space-y-4">
            <TabsList>
              <TabsTrigger value="library">Library</TabsTrigger>
              <TabsTrigger value="embeddings">Embeddings</TabsTrigger>
              <TabsTrigger value="analytics">Analytics</TabsTrigger>
            </TabsList>

            <TabsContent value="library" className="space-y-4">
              {/* Search and Filter */}
              <div className="flex gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                    <Input
                      placeholder="Search documents..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 border border-slate-300 rounded-md text-sm"
                >
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category === "all" ? "All Categories" : category}
                    </option>
                  ))}
                </select>
              </div>

              {/* Document List */}
              <ScrollArea className="h-[400px]">
                <div className="space-y-3">
                  {filteredDocuments.map((doc) => (
                    <Card key={doc.id} className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1">
                          <FileText className="w-8 h-8 text-slate-400" />
                          <div className="flex-1">
                            <h4 className="font-medium text-sm">{doc.name}</h4>
                            <div className="flex items-center gap-4 text-xs text-slate-500 mt-1">
                              <span className="flex items-center gap-1">
                                <Tag className="w-3 h-3" />
                                {doc.category}
                              </span>
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {doc.uploadDate}
                              </span>
                              <span>{doc.size}</span>
                              {doc.embeddings > 0 && (
                                <span className="flex items-center gap-1">
                                  <Database className="w-3 h-3" />
                                  {doc.embeddings} embeddings
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {getStatusBadge(doc.status)}
                          <Button size="sm" variant="outline">
                            <Eye className="w-3 h-3 mr-1" />
                            View
                          </Button>
                          <Button size="sm" variant="outline">
                            <Download className="w-3 h-3 mr-1" />
                            Download
                          </Button>
                          <Button size="sm" variant="outline">
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            </TabsContent>

            <TabsContent value="embeddings">
              <Card className="p-6">
                <div className="text-center">
                  <Database className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                  <h3 className="text-lg font-medium mb-2">Vector Embeddings</h3>
                  <p className="text-slate-600 mb-4">
                    Total embeddings stored in Pinecone: <strong>3,595</strong>
                  </p>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="p-3 bg-slate-50 rounded">
                      <p className="font-medium">Processed</p>
                      <p className="text-2xl font-bold text-green-600">3,595</p>
                    </div>
                    <div className="p-3 bg-slate-50 rounded">
                      <p className="font-medium">Processing</p>
                      <p className="text-2xl font-bold text-yellow-600">0</p>
                    </div>
                    <div className="p-3 bg-slate-50 rounded">
                      <p className="font-medium">Failed</p>
                      <p className="text-2xl font-bold text-red-600">0</p>
                    </div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            <TabsContent value="analytics">
              <Card className="p-6">
                <div className="text-center">
                  <p className="text-slate-600">Document analytics and usage statistics coming soon...</p>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
