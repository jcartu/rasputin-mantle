'use client';

import * as React from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function ProjectKnowledgeRoute() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  React.useEffect(() => {
    router.replace(`/projects/${params.id}`);
  }, [params.id, router]);
  return null;
}
