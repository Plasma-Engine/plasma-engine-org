'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/stores/auth';
import { Center, Loader, Stack, Text } from '@mantine/core';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.push('/dashboard');
      } else {
        router.push('/auth/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <Center style={{ height: '100vh' }}>
      <Stack align="center" gap="md">
        <Loader size="lg" color="blue" />
        <Text size="lg" c="dimmed">
          Redirecting to Plasma Engine...
        </Text>
      </Stack>
    </Center>
  );
}
  );
}
