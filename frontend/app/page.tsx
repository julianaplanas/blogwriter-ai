"use client"

import { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Copy, Download } from "lucide-react"
import ReactMarkdown from "react-markdown"

// API Base URL - use environment variable in production, fallback to localhost for development
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

interface BlogMetadata {
  word_count: number
  sources_count: number
  images_count: number
}

interface SavedPost {
  id: string
  topic: string
  word_count: number
  sources_count: number
  images_count: number
  created_at: string
  updated_at: string
}

interface BlogResponse {
  id: string
  markdown: string
  references: Array<{ title: string; url: string }>
  images: Array<{ url: string; alt_text: string }>
  metadata: BlogMetadata
}

interface EditInfo {
  changes_summary?: string
  diff_text?: string
  model_used?: string
  provider_used?: string
  edited_at?: string
  instruction_applied?: string
}

export default function AIBlogWriter() {
  const [topic, setTopic] = useState("")
  const [markdown, setMarkdown] = useState("")
  const [editInstruction, setEditInstruction] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [isReverting, setIsReverting] = useState(false)
  const [metadata, setMetadata] = useState<BlogMetadata | null>(null)
  const [references, setReferences] = useState<Array<{ title: string; url: string }>>([])
  const [images, setImages] = useState<Array<{ url: string; alt_text: string }>>([])
  const [editInfo, setEditInfo] = useState<EditInfo | null>(null)
  const [showEditDetails, setShowEditDetails] = useState(false)
  const [versionHistory, setVersionHistory] = useState<any[]>([])
  const [currentPostId, setCurrentPostId] = useState<string | null>(null)
  const [currentVersionId, setCurrentVersionId] = useState<string | null>(null)
  const [actualCurrentVersionId, setActualCurrentVersionId] = useState<string | null>(null)
  const [hasUsedUndo, setHasUsedUndo] = useState(false)
  const [savedPosts, setSavedPosts] = useState<SavedPost[]>([])
  const [loadingSavedPosts, setLoadingSavedPosts] = useState(false)
  const [showSavedPosts, setShowSavedPosts] = useState(false)
  const { toast } = useToast()

  // Clean markdown from image placeholders and other artifacts
  const cleanMarkdown = (markdown: string): string => {
    return markdown
      .replace(/<!-- IMAGE:.*?-->/gi, '') // Remove image placeholder comments
      .replace(/<!-- .*? -->/gi, '') // Remove any other HTML comments
      .replace(/={3,}/g, '') // Remove lines of equal signs (============)
      .replace(/\-{3,}/g, '---') // Convert long dash lines to standard markdown horizontal rule  
      .replace(/^\s*={3,}\s*$/gm, '') // Remove lines that are only equal signs
      .replace(/^\s*\-{4,}\s*$/gm, '---') // Convert lines of dashes to standard markdown horizontal rule
      .replace(/^\s*={10,}.*$/gm, '') // Remove any line starting with 10+ equal signs
      .replace(/^\s*\-{10,}.*$/gm, '') // Remove any line starting with 10+ dashes
      .replace(/\n={5,}[^\n]*\n/g, '\n\n') // Remove lines with 5+ equal signs as separators
      .replace(/\n\-{5,}[^\n]*\n/g, '\n\n') // Remove lines with 5+ dashes as separators
      .replace(/\n\n\n+/g, '\n\n') // Remove excessive line breaks
      .replace(/^\s*\n/gm, '\n') // Remove lines with only whitespace
      .trim()
  }

  // Clear version history when component mounts
  useEffect(() => {
    setVersionHistory([])
    setCurrentVersionId(null)
    setActualCurrentVersionId(null)
    setHasUsedUndo(false)
  }, [])

  // Function to fetch saved blog posts
  const fetchSavedPosts = async () => {
    setLoadingSavedPosts(true)
    try {
      const response = await fetch(`${API_BASE_URL}/posts`)
      if (!response.ok) throw new Error("Failed to fetch saved posts")
      
      const data = await response.json()
      console.log("Posts data:", data) // Debug log
      
      // Backend returns: {posts: [...], count: number, status: string}
      const posts = (data.posts || []).map((post: any) => ({
        id: post.id,
        topic: post.topic,
        word_count: post.word_count || 0,
        sources_count: 0, // Backend doesn't track this separately yet
        images_count: 0,  // Backend doesn't track this separately yet
        created_at: post.created_at,
        updated_at: post.created_at // Use created_at as fallback
      }))
      
      setSavedPosts(posts)
    } catch (error) {
      console.error("Error fetching saved posts:", error)
      toast({
        title: "Failed to load saved posts",
        variant: "destructive",
      })
    } finally {
      setLoadingSavedPosts(false)
    }
  }

  // Function to load a saved blog post
  const loadSavedPost = async (postId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/post/${postId}`)
      if (!response.ok) throw new Error("Failed to load blog post")
      
      const post = await response.json()
      console.log("Loaded post:", post) // Debug log
      
      // Set the blog content - backend returns: id, topic, content, word_count, created_at, metadata
      setTopic(post.topic)
      setMarkdown(post.content)
      setCurrentPostId(postId)
      
      // Try to extract sources and images from metadata if available
      let sources = []
      let images = []
      
      if (post.metadata) {
        try {
          const metadata = typeof post.metadata === 'string' ? JSON.parse(post.metadata) : post.metadata
          if (metadata.sources) {
            sources = metadata.sources.map((source: any) => ({
              title: source.title || "Untitled",
              url: source.url || "#"
            }))
          }
          if (metadata.images) {
            images = metadata.images.map((image: any) => ({
              url: image.medium_url || image.url || "",
              alt_text: image.alt || image.photographer || "Blog image"
            }))
          }
        } catch (e) {
          console.error("Error parsing metadata:", e)
        }
      }
      
      setReferences(sources)
      setImages(images)
      
      // Set metadata
      setMetadata({
        word_count: post.word_count || post.content.split(/\s+/).length,
        sources_count: sources.length,
        images_count: images.length
      })
      
      // Clear edit info
      setEditInfo(null)
      setShowEditDetails(false)
      setHasUsedUndo(false)
      setVersionHistory([])
      
      // Close saved posts dialog
      setShowSavedPosts(false)
      
      toast({
        title: "Blog post loaded",
        description: `Loaded: ${post.topic}`,
      })
    } catch (error) {
      console.error("Error loading saved post:", error)
      toast({
        title: "Failed to load blog post",
        variant: "destructive",
      })
    }
  }

  // Function to delete a saved blog post  
  const deleteSavedPost = async (postId: string, postTopic: string) => {
    if (!confirm(`Are you sure you want to delete "${postTopic}"?`)) return
    
    try {
      const response = await fetch(`${API_BASE_URL}/post/${postId}`, {
        method: "DELETE"
      })
      
      if (!response.ok) throw new Error("Failed to delete blog post")
      
      // Remove from saved posts list
      setSavedPosts(posts => posts.filter(p => p.id !== postId))
      
      toast({
        title: "Blog post deleted",
        description: `Deleted: ${postTopic}`,
      })
    } catch (error) {
      console.error("Error deleting saved post:", error)
      toast({
        title: "Failed to delete blog post",
        variant: "destructive",
      })
    }
  }

  const handleGenerate = async () => {
    if (!topic.trim() || topic.length < 3) {
      toast({
        title: "Please enter a topic with at least 3 characters",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    
    // Clear version history for new post
    await clearVersionHistory()
    
    try {
      // Use the enhanced endpoint that includes research and images
      const response = await fetch(`${API_BASE_URL}/generate-enhanced`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("Backend response:", data) // Debug log
      
      // The backend returns: content, sources, images, metadata
      const cleanedMarkdown = cleanMarkdown(data.content)
      setMarkdown(cleanedMarkdown)
      setCurrentPostId(data.id)
      
      // Handle sources (research results)
      const references = (data.sources || []).map((source: any) => ({
        title: source.title || "Untitled",
        url: source.url || "#"
      }))
      setReferences(references)
      
      // Handle images
      const formattedImages = (data.images || []).map((image: any) => ({
        url: image.medium_url || image.url || "",
        alt_text: image.alt || image.photographer || "Blog image"
      }))
      setImages(formattedImages)
      
      // Set metadata
      setMetadata({
        word_count: data.word_count || data.content.split(/\s+/).length,
        sources_count: references.length,
        images_count: formattedImages.length
      })

      // Create initial version in backend by tracking this as first version
      try {
        await fetch(`${API_BASE_URL}/edit`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content: cleanedMarkdown,
            instruction: "Initial version - no changes",
          }),
        })
        
        // Fetch version history to get the initial version
        await fetchVersionHistory()
      } catch (error) {
        console.error("Failed to create initial version:", error)
      }

      // Clear previous edit info
      setEditInfo(null)
      setShowEditDetails(false)
      setHasUsedUndo(false) // Reset undo state for new post

      toast({
        title: `Generated ${data.word_count} words with ${references.length} sources and ${formattedImages.length} images`,
      })
    } catch (error) {
      console.error("Generation error:", error)
      toast({
        title: "Backend not running. Please start the FastAPI server.",
        variant: "destructive",
      })

      // Mock response for demo purposes
      const mockMarkdown = `# ${topic.charAt(0).toUpperCase() + topic.slice(1)}

![Hero Image](/placeholder.svg?height=300&width=600&query=${encodeURIComponent(topic)})

## Introduction

This comprehensive guide explores the fascinating world of ${topic}, covering the latest developments, key insights, and future implications.

## Key Points

- **Innovation**: Revolutionary approaches are transforming the landscape
- **Impact**: Significant effects on industry and society
- **Future**: Promising developments on the horizon

## Deep Dive Analysis

The field of ${topic} has experienced remarkable growth in recent years. Experts predict continued expansion and innovation in this area.

### Current Trends

1. **Technology Integration**: Advanced systems are becoming more sophisticated
2. **Market Adoption**: Widespread acceptance across various sectors
3. **Research Breakthroughs**: New discoveries are pushing boundaries

## Conclusion

As we look toward the future, ${topic} will undoubtedly play a crucial role in shaping our world. The potential for positive impact remains enormous.

---

*This article was generated using AI research and analysis.*`

      const mockReferences = [
        { title: "Industry Report on " + topic, url: "https://example.com/report1" },
        { title: "Latest Research in " + topic, url: "https://example.com/research" },
        { title: "Expert Analysis: " + topic, url: "https://example.com/analysis" }
      ]

      const cleanedMockMarkdown = cleanMarkdown(mockMarkdown)
      setMarkdown(cleanedMockMarkdown)
      setReferences(mockReferences)
      setImages([])
      setCurrentPostId("mock-post-" + Date.now())
      setMetadata({
        word_count: 234,
        sources_count: mockReferences.length,
        images_count: 1,
      })

      // Clear previous edit info for new post
      setEditInfo(null)
      setShowEditDetails(false)
      setHasUsedUndo(false) // Reset undo state for new post
    } finally {
      setIsGenerating(false)
    }
  }

  const handleEdit = async () => {
    console.log("Edit button clicked!", { editInstruction, isEditing }); // Debug log
    
    if (!editInstruction.trim() || editInstruction.length < 5) {
      toast({
        title: "Please provide editing instructions with at least 5 characters",
        variant: "destructive",
      })
      return
    }

    setIsEditing(true)
    try {
      console.log("Sending edit request to:", `${API_BASE_URL}/edit`); // Debug log
      
      const response = await fetch(`${API_BASE_URL}/edit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: markdown,
          instruction: editInstruction,
        }),
      })

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Edit failed:", response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("Edit response:", data) // Debug log
      
      // Update markdown content and clean it
      const cleanedMarkdown = cleanMarkdown(data.content)
      setMarkdown(cleanedMarkdown)
      setEditInstruction("")
      
      // Store detailed edit information
      setEditInfo({
        changes_summary: `Edited with instruction: "${data.instruction_applied}"`,
        model_used: data.model_used,
        provider_used: data.provider_used,
        edited_at: data.edited_at,
        instruction_applied: data.instruction_applied
      })
      
      // Update word count
      if (metadata) {
        const newWordCount = data.content.split(/\s+/).length
        setMetadata({
          ...metadata,
          word_count: newWordCount
        })
      }

      toast({
        title: "Blog post edited successfully",
        description: `Applied: ${data.instruction_applied}`
      })

      // Refresh version history after successful edit
      setTimeout(async () => {
        await fetchVersionHistory()
      }, 100)
      
    } catch (error) {
      console.error("Edit error:", error)
      toast({
        title: "Failed to edit blog post",
        description: "Please check your connection and try again.",
        variant: "destructive",
      })
    } finally {
      setIsEditing(false)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(markdown)
    toast({
      title: "Copied to clipboard",
    })
  }

  const downloadMarkdown = () => {
    const blob = new Blob([markdown], { type: "text/markdown" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `${topic.replace(/\s+/g, "-").toLowerCase()}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Downloaded successfully",
    })
  }

  const fetchVersionHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/edit/history`)
      if (response.ok) {
        const data = await response.json()
        setVersionHistory(data.versions || [])
        const currentVersion = data.current_version || null
        setCurrentVersionId(currentVersion)
        setActualCurrentVersionId(currentVersion)
      } else {
        console.error("Failed to fetch version history:", response.status)
        setVersionHistory([])
        setCurrentVersionId(null)
        setActualCurrentVersionId(null)
      }
    } catch (error) {
      console.error("Failed to fetch version history:", error)
      setVersionHistory([])
      setCurrentVersionId(null)
      setActualCurrentVersionId(null)
    }
  }

  const clearVersionHistory = async () => {
    try {
      await fetch(`${API_BASE_URL}/edit/history`, {
        method: "DELETE"
      })
      setVersionHistory([])
      setCurrentVersionId(null)
      setActualCurrentVersionId(null)
      setHasUsedUndo(false)
    } catch (error) {
      console.error("Failed to clear version history:", error)
    }
  }

  const handleUndo = async () => {
    if (versionHistory.length < 2) {
      toast({
        title: "No previous version available",
        variant: "destructive",
      })
      return
    }

    // Get all versions sorted by timestamp (oldest first)
    const sortedVersions = [...versionHistory].sort((a, b) => 
      new Date(a.timestamp || a.edited_at || 0).getTime() - new Date(b.timestamp || b.edited_at || 0).getTime()
    )
    
    // Find current version index
    const currentIndex = sortedVersions.findIndex(v => v.version_id === actualCurrentVersionId)
    
    // Get the previous version (one before current)
    const previousVersion = currentIndex > 0 ? sortedVersions[currentIndex - 1] : sortedVersions[sortedVersions.length - 2]
    
    if (!previousVersion?.version_id) {
      toast({
        title: "No previous version found",
        variant: "destructive",
      })
      return
    }

    console.log("=== UNDO DEBUG ===")
    console.log("Current version:", actualCurrentVersionId)
    console.log("Target version:", previousVersion.version_id)
    console.log("All versions:", sortedVersions.map(v => ({id: v.version_id, instruction: v.instruction})))

    setIsReverting(true)
    try {
      const response = await fetch(`${API_BASE_URL}/edit/undo/${previousVersion.version_id}`, {
        method: "POST",
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      console.log("Undo API response:", {
        version_restored: data.version_restored,
        content_length: data.content?.length,
        first_100_chars: data.content?.substring(0, 100)
      })
      
      // Store current markdown for comparison
      const beforeMarkdown = markdown
      
      const cleanedMarkdown = cleanMarkdown(data.content)
      console.log("Before setMarkdown - current:", beforeMarkdown.substring(0, 100))
      console.log("Before setMarkdown - new:", cleanedMarkdown.substring(0, 100))
      
      setMarkdown(cleanedMarkdown)
      
      console.log("After setMarkdown called")
      
      // Update word count
      if (metadata) {
        const newWordCount = cleanedMarkdown.split(/\s+/).length
        setMetadata({
          ...metadata,
          word_count: newWordCount
        })
      }

      // Clear edit info since we reverted
      setEditInfo(null)
      setShowEditDetails(false)
      
      // Mark that undo has been used
      setHasUsedUndo(true)

      toast({
        title: "Reverted to previous version",
        description: `Restored version: ${data.version_restored || previousVersion.version_id}`,
      })

      // Refresh version history
      setTimeout(async () => {
        await fetchVersionHistory()
        console.log("Version history refreshed")
      }, 100)

    } catch (error) {
      console.error("Undo error:", error)
      toast({
        title: "Failed to revert changes",
        variant: "destructive",
      })
    } finally {
      setIsReverting(false)
    }
  }

  // Load saved posts when component mounts
  useEffect(() => {
    fetchSavedPosts()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-orange-50">
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">AI</span>
            </div>
            <span className="text-2xl font-medium text-black">Blog Writer</span>
          </div>

          <h1 className="text-5xl font-medium text-black mb-8 leading-tight">Write with AI</h1>

          {/* Topic Input */}
          <div className="max-w-2xl mx-auto mb-8">
            <div className="relative">
              <textarea
                placeholder="Enter your blog post topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full px-6 py-4 pr-32 text-lg bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent placeholder-gray-500 resize-none min-h-[60px] max-h-[100px]"
                maxLength={200}
                rows={1}
                style={{
                  height: 'auto',
                  minHeight: '60px',
                  maxHeight: '100px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 100) + 'px';
                }}
              />
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !topic.trim()}
                className="absolute right-2 top-2 px-6 py-2 bg-black text-white rounded-xl hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="hidden sm:inline">Generating...</span>
                  </>
                ) : (
                  "Generate"
                )}
              </button>
            </div>

            {isGenerating && <p className="text-gray-600 text-sm mt-4">Researching and generating content...</p>}
            
            {/* Saved Posts Button */}
            <div className="text-center mt-6">
              <button
                onClick={() => {
                  setShowSavedPosts(true)
                  fetchSavedPosts()
                }}
                className="px-6 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-all duration-200 flex items-center gap-2 mx-auto"
              >
                Load Saved Posts
              </button>
            </div>
          </div>
        </div>

        {/* Content Area */}
        {markdown && (
          <div className="space-y-12">
            {/* Edit Section */}
            <div className="max-w-2xl mx-auto">
              <div className="relative">
                <textarea
                  placeholder="How would you like to edit this?"
                  value={editInstruction}
                  onChange={(e) => setEditInstruction(e.target.value)}
                  className="w-full px-6 py-4 pr-20 text-lg bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent placeholder-gray-500 resize-none min-h-[60px] max-h-[120px]"
                  rows={1}
                  style={{
                    height: 'auto',
                    minHeight: '60px',
                    maxHeight: '120px'
                  }}
                  onInput={(e) => {
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                  }}
                />
                <button
                  onClick={handleEdit}
                  disabled={isEditing || !editInstruction.trim()}
                  className="absolute right-2 top-2 px-6 py-2 bg-black text-white rounded-xl hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
                >
                  {isEditing ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span className="hidden sm:inline">Editing...</span>
                    </>
                  ) : (
                    "Edit"
                  )}
                </button>
              </div>

              {isEditing && <p className="text-gray-600 text-sm mt-4 text-center">Applying edits...</p>}
            </div>

            {/* Actions */}
            <div className="flex justify-center gap-4">
              <button
                onClick={copyToClipboard}
                className="flex items-center gap-2 px-6 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-full hover:bg-white transition-all duration-200"
              >
                <Copy className="h-4 w-4" />
                Copy
              </button>
              <button
                onClick={downloadMarkdown}
                className="flex items-center gap-2 px-6 py-3 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-full hover:bg-white transition-all duration-200"
              >
                <Download className="h-4 w-4" />
                Download
              </button>
            </div>

            {/* Enhanced Stats */}
            {metadata && (
              <div className="text-center space-y-2">
                <p className="text-gray-600 text-sm">
                  {metadata.word_count} words • {metadata.sources_count} sources • {metadata.images_count} images
                </p>
                {editInfo?.edited_at && (
                  <p className="text-gray-500 text-xs">
                    Last edited: {new Date(editInfo.edited_at).toLocaleString()} 
                    {editInfo.model_used && ` • ${editInfo.model_used}`}
                  </p>
                )}
              </div>
            )}

            {/* Content Preview */}
            <div className="bg-white/60 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-gray-200">
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown
                  components={{
                    img: ({ src, alt }) => {
                      // Handle different types of images
                      let imgSrc = src || "/placeholder.svg"
                      
                      // If it's an Unsplash URL that might be blocked, use placeholder
                      if (src?.includes('unsplash.com')) {
                        imgSrc = "/placeholder.svg"
                      }
                      // If it's a Pexels URL, use it directly
                      else if (src?.includes('pexels.com')) {
                        imgSrc = src
                      }
                      
                      return (
                        <img
                          src={imgSrc}
                          alt={alt || "Blog image"}
                          className="rounded-2xl shadow-sm max-w-full h-auto my-8"
                          onError={(e) => {
                            // Fallback to placeholder if image fails to load
                            const target = e.target as HTMLImageElement
                            if (target.src !== "/placeholder.svg") {
                              target.src = "/placeholder.svg"
                            }
                          }}
                          loading="lazy"
                        />
                      )
                    },
                    h1: ({ children }) => (
                      <h1 className="text-4xl font-medium text-black mb-8 leading-tight">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-3xl font-medium text-black mb-6 mt-12 leading-tight">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-2xl font-medium text-black mb-4 mt-8 leading-tight">{children}</h3>
                    ),
                    p: ({ children }) => <p className="text-gray-700 mb-6 leading-relaxed text-lg">{children}</p>,
                    ul: ({ children }) => (
                      <ul className="list-disc list-inside mb-6 text-gray-700 space-y-2">{children}</ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside mb-6 text-gray-700 space-y-2">{children}</ol>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-black pl-6 italic text-gray-700 mb-6 text-lg">
                        {children}
                      </blockquote>
                    ),
                    code: ({ children }) => (
                      <code className="bg-gray-100 px-3 py-1 rounded-lg text-sm font-mono">{children}</code>
                    ),
                    hr: () => <hr className="border-gray-200 my-12" />,
                  }}
                >
                  {markdown}
                </ReactMarkdown>
              </div>
            </div>

            {/* Images Section */}
            {images.length > 0 && (
              <div className="max-w-2xl mx-auto mt-8">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="font-medium text-gray-900 mb-4">Related Images</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {images.map((image, index) => (
                      <div key={index} className="space-y-2">
                        <img
                          src={image.url}
                          alt={image.alt_text}
                          className="w-full h-32 object-cover rounded-lg border border-gray-200"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement
                            target.src = "/placeholder.svg"
                          }}
                          loading="lazy"
                        />
                        <p className="text-xs text-gray-600 truncate">{image.alt_text}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sources/References Section */}
            {references.length > 0 && (
              <div className="max-w-2xl mx-auto mt-8">
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="font-medium text-gray-900 mb-4">Sources & References</h3>
                  <div className="space-y-3">
                    {references.map((ref, index) => (
                      <div key={index} className="border-l-4 border-blue-500 pl-4">
                        <a
                          href={ref.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 font-medium text-sm block"
                        >
                          {ref.title}
                        </a>
                        <p className="text-xs text-gray-500 mt-1 truncate">{ref.url}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Enhanced Edit Details */}
            {editInfo && (
              <div className="max-w-2xl mx-auto">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-blue-900">Latest Edit Details</h3>
                    <button
                      onClick={() => setShowEditDetails(!showEditDetails)}
                      className="text-blue-700 hover:text-blue-900 text-sm"
                    >
                      {showEditDetails ? 'Hide Details' : 'Show Details'}
                    </button>
                  </div>
                  
                  {editInfo.changes_summary && (
                    <div className="text-sm text-blue-800 mb-2">
                      <strong>Applied:</strong> "{editInfo.instruction_applied}"
                    </div>
                  )}
                  
                  {editInfo.changes_summary && showEditDetails && (
                    <div className="mt-3 space-y-2">
                      <div className="text-sm">
                        <strong className="text-blue-900">Changes Summary:</strong>
                        <div className="bg-white rounded p-2 mt-1 font-mono text-xs">
                          {editInfo.changes_summary.split('\n').map((line, i) => (
                            <div key={i}>{line}</div>
                          ))}
                        </div>
                      </div>
                      
                      {editInfo.diff_text && (
                        <div className="text-sm">
                          <strong className="text-blue-900">Changes Diff:</strong>
                          <div className="bg-gray-900 text-green-400 rounded p-2 mt-1 font-mono text-xs max-h-32 overflow-y-auto">
                            <pre className="whitespace-pre-wrap">{editInfo.diff_text}</pre>
                          </div>
                        </div>
                      )}
                      
                      <div className="flex justify-between items-center text-xs text-blue-700 mt-2">
                        <span>Model: {editInfo.model_used} ({editInfo.provider_used})</span>
                        <span>Edited: {editInfo.edited_at ? new Date(editInfo.edited_at).toLocaleTimeString() : ''}</span>
                      </div>
                      
                      {/* Undo Button */}
                      <div className="mt-3 pt-2 border-t border-blue-200">
                        <button
                          onClick={handleUndo}
                          disabled={isReverting || versionHistory.length < 2 || hasUsedUndo}
                          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center justify-center gap-2"
                        >
                          {isReverting ? (
                            <>
                              <Loader2 className="h-4 w-4 animate-spin" />
                              Reverting...
                            </>
                          ) : hasUsedUndo ? (
                            "Undo Already Used"
                          ) : (
                            <>
                              Undo Last Edit
                            </>
                          )}
                        </button>
                        {versionHistory.length < 2 && !hasUsedUndo && (
                          <p className="text-xs text-blue-600 mt-1 text-center">No previous version available</p>
                        )}
                        {hasUsedUndo && (
                          <p className="text-xs text-blue-600 mt-1 text-center">Make another edit to enable undo</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Version History */}
            <div className="max-w-2xl mx-auto">
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">Version History</h3>
                  {versionHistory.length >= 2 && !hasUsedUndo && (
                    <button
                      onClick={handleUndo}
                      disabled={isReverting}
                      className="px-3 py-2 text-sm rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2"
                    >
                      {isReverting ? (
                        <>
                          <Loader2 className="h-3 w-3 animate-spin" />
                          Reverting...
                        </>
                      ) : (
                        <>
                          Undo Last Edit
                        </>
                      )}
                    </button>
                  )}
                  {hasUsedUndo && (
                    <div className="px-3 py-2 text-sm text-gray-400 bg-gray-100 rounded-lg">
                      Undo Used
                    </div>
                  )}
                </div>
                
                {versionHistory.length === 0 ? (
                  <p className="text-gray-500 text-sm text-center py-4">No version history available</p>
                ) : (
                  <div className="space-y-3">
                    {versionHistory.slice().reverse().map((version, index) => {
                      const isCurrentVersion = version.version_id === actualCurrentVersionId
                      return (
                        <div key={version.version_id} className="p-4 rounded-lg bg-white shadow-sm border">
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="font-medium text-gray-900 text-sm">
                                  {version.version_id}
                                </span>
                                {isCurrentVersion && (
                                  <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                                    Current
                                  </span>
                                )}
                              </div>
                              
                              {version.instruction && version.instruction !== "Initial version - no changes" && (
                                <div className="mb-3">
                                  <p className="text-sm font-medium text-gray-700 mb-1">Edit Instruction:</p>
                                  <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded italic">
                                    "{version.instruction}"
                                  </p>
                                </div>
                              )}
                              
                              {(!version.instruction || version.instruction === "Initial version - no changes") && (
                                <div className="mb-3">
                                  <p className="text-sm font-medium text-gray-500 mb-1">Original Version</p>
                                  <p className="text-xs text-gray-500">First generated content</p>
                                </div>
                              )}
                              
                              <p className="text-xs text-gray-500">
                                {version.timestamp ? 
                                  new Date(version.timestamp).toLocaleString() : 
                                  (version.edited_at ? new Date(version.edited_at).toLocaleString() : 'Unknown date')
                                }
                              </p>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Saved Posts Modal */}
        {showSavedPosts && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">Saved Blog Posts</h2>
                  <button
                    onClick={() => setShowSavedPosts(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    ×
                  </button>
                </div>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
                {loadingSavedPosts ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-8 w-8 animate-spin" />
                    <span className="ml-3 text-gray-600">Loading saved posts...</span>
                  </div>
                ) : savedPosts.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <p>No saved blog posts yet.</p>
                    <p className="text-sm mt-2">Generate your first blog post to get started!</p>
                  </div>
                ) : (
                  <div className="grid gap-4">
                    {savedPosts.map((post) => (
                      <div
                        key={post.id}
                        className="border border-gray-200 rounded-xl p-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-medium text-lg mb-2">{post.topic}</h3>
                            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
                              <span>{post.word_count} words</span>
                              <span>{post.sources_count} sources</span>
                              <span>{post.images_count} images</span>
                              <span>{new Date(post.created_at).toLocaleDateString()}</span>
                            </div>
                            {post.updated_at !== post.created_at && (
                              <div className="text-xs text-orange-600 mb-2">
                                Updated: {new Date(post.updated_at).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                          <div className="flex gap-2 ml-4">
                            <button
                              onClick={() => loadSavedPost(post.id)}
                              className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors text-sm"
                            >
                              Load
                            </button>
                            <button
                              onClick={() => deleteSavedPost(post.id, post.topic)}
                              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t border-gray-200 bg-gray-50">
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-600">
                    {savedPosts.length} saved post{savedPosts.length !== 1 ? 's' : ''}
                  </div>
                  <button
                    onClick={() => fetchSavedPosts()}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                  >
                    Refresh
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
