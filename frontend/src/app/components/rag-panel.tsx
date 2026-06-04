import { motion } from "motion/react";
import { Search, Database, Zap, ExternalLink } from "lucide-react";
import { useState } from "react";

export function RAGPanel() {
  const [query, setQuery] = useState("");

  const knowledgeResults = [
    {
      id: 1,
      title: "COBOL PICTURE Clause Specification",
      source: "IBM COBOL Language Reference",
      similarity: 0.94,
      excerpt:
        "The PICTURE clause specifies the general characteristics and editing requirements of an elementary item...",
      color: "var(--neon-blue)",
    },
    {
      id: 2,
      title: "Python Dataclass Best Practices",
      source: "Python Enhancement Proposals (PEP 557)",
      similarity: 0.91,
      excerpt:
        "Dataclasses provide a decorator and functions for automatically adding generated special methods...",
      color: "var(--neon-purple)",
    },
    {
      id: 3,
      title: "Financial Precision with Decimal Type",
      source: "Python Standard Library Documentation",
      similarity: 0.88,
      excerpt:
        "The decimal module provides support for fast correctly rounded decimal floating point arithmetic...",
      color: "var(--neon-emerald)",
    },
  ];

  return (
    <div className="py-12 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-8"
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--neon-blue)] to-[var(--neon-purple)] flex items-center justify-center">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <h3 className="mb-1">RAG Knowledge Retrieval</h3>
              <p className="text-sm text-[var(--muted-foreground)]">
                Semantic search across documentation and code patterns
              </p>
            </div>
          </div>

          <div className="relative mb-8">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[var(--muted-foreground)]" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search knowledge base for patterns, documentation, examples..."
              className="w-full pl-12 pr-4 py-4 rounded-xl glass border-0 focus:ring-2 focus:ring-[var(--neon-blue)] transition-all"
            />
            <motion.div
              className="absolute right-3 top-1/2 transform -translate-y-1/2"
              whileHover={{ scale: 1.1 }}
            >
              <Zap className="w-5 h-5 text-[var(--neon-blue)]" />
            </motion.div>
          </div>

          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-[var(--muted-foreground)]">
                Relevant Knowledge Chunks
              </span>
              <span className="text-xs text-[var(--muted-foreground)]">
                Vector similarity search
              </span>
            </div>

            <div className="grid grid-cols-3 gap-3 mb-6">
              {knowledgeResults.map((result, index) => (
                <motion.div
                  key={result.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="h-2 rounded-full overflow-hidden bg-[var(--input-background)]"
                >
                  <motion.div
                    className="h-full"
                    style={{ background: result.color }}
                    initial={{ width: 0 }}
                    animate={{ width: `${result.similarity * 100}%` }}
                    transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                  />
                </motion.div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {knowledgeResults.map((result, index) => (
              <motion.div
                key={result.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + index * 0.1 }}
                className="p-4 rounded-xl bg-[var(--input-background)] hover:bg-[var(--muted)] transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ background: result.color }}
                    />
                    <h4 className="text-sm group-hover:text-[var(--neon-blue)] transition-colors">
                      {result.title}
                    </h4>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-[var(--muted-foreground)]">
                      {(result.similarity * 100).toFixed(0)}% match
                    </span>
                    <ExternalLink className="w-3 h-3 text-[var(--muted-foreground)] opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>

                <p className="text-xs text-[var(--muted-foreground)] mb-2">
                  {result.excerpt}
                </p>

                <div className="flex items-center gap-2">
                  <Database className="w-3 h-3 text-[var(--muted-foreground)]" />
                  <span className="text-xs text-[var(--muted-foreground)]">
                    {result.source}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-[var(--neon-blue)]/10 to-[var(--neon-purple)]/10 border border-[var(--neon-blue)]/20">
            <div className="flex items-start gap-3">
              <Zap className="w-5 h-5 text-[var(--neon-blue)] flex-shrink-0 mt-0.5" />
              <div className="text-xs text-[var(--muted-foreground)]">
                <span className="text-[var(--foreground)]">Vector embeddings:</span> Using
                sentence-transformers/all-MiniLM-L6-v2 with 384-dimensional embeddings.
                Index contains 147,532 documentation chunks from COBOL specs, Python docs,
                and modernization patterns.
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
