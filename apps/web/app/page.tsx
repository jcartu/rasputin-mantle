import { Sidebar } from "@/components/sidebar";

export default function HomePage() {
  return (
    <>
      <Sidebar />
      <main className="flex-1 flex items-center justify-center bg-zinc-950">
        <div className="text-zinc-500 text-lg">
          Select a session or create a new one
        </div>
      </main>
    </>
  );
}
