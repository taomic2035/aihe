"use client"
import { useEffect, useState } from "react"

export default function MemoriesPage() {
  const [mems, setMems] = useState<any[]>([])
  const userId = "demo"
  useEffect(() => {
    fetch(`/v1/memories?user_id=${userId}`).then(r=>r.json()).then(d=>setMems(d.memories||[]))
  }, [])
  const onDelete = async (id: string) => {
    await fetch(`/v1/memories/${id}?user_id=${userId}`, { method: "DELETE" })
    setMems(mems.filter(m=>m.id!==id))
  }
  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">记忆审计面板</h1>
      <p className="text-sm text-gray-500">用户可查看/删除单条记忆，验证删除后不再被召回</p>
      <ul className="mt-4 space-y-2">
        {mems.map(m=>(
          <li key={m.id} className="border p-2 flex justify-between">
            <span>{m.content}</span>
            <button onClick={()=>onDelete(m.id)} className="text-red-500">删除</button>
          </li>
        ))}
      </ul>
    </div>
  )
}
