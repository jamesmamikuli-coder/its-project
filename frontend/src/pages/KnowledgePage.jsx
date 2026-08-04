import React, { useEffect, useState } from "react";
import { articleAPI } from "../api/api";

export default function KnowledgePage() {

  const [articles, setArticles] = useState([]);
  const [search, setSearch] = useState("");


  // LOAD ARTICLES FROM BACKEND
  useEffect(() => {
    loadArticles();
  }, []);


  const loadArticles = async () => {
    try {
      const res = await articleAPI.getArticles();
      setArticles(res.data.articles);
    } catch (error) {
      console.log("Error loading articles:", error);
    }
  };


  // FILTER SEARCH
  const filtered = articles.filter((a) =>
    a.title.toLowerCase().includes(search.toLowerCase())
  );


  return (
    <div style={{ padding: 20 }}>

      <h2>📚 Knowledge Base</h2>

      {/* SEARCH BOX */}
      <input
        type="text"
        placeholder="Search articles..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{
          width: "60%",
          padding: 10,
          marginBottom: 20
        }}
      />

      {/* ARTICLES */}
      {filtered.map((article) => (
        <div
          key={article.id}
          style={{
            border: "1px solid #ddd",
            padding: 15,
            marginBottom: 10,
            borderRadius: 8,
            background: "#f9f9f9"
          }}
        >
          <h3>{article.title}</h3>
          <p>{article.content}</p>
        </div>
      ))}

    </div>
  );
}