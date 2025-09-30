'use client';

import { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  Text,
  Title,
  Group,
  Stack,
  Badge,
  Progress,
  SimpleGrid,
  ActionIcon,
  Box,
  Center,
  RingProgress,
  ThemeIcon,
  Skeleton,
  Alert,
  Button,
} from '@mantine/core';
import {
  IconArrowUp,
  IconArrowDown,
  IconSearch,
  IconBrandTwitter,
  IconEdit,
  IconRobot,
  IconActivity,
  IconTrendingUp,
  IconUsers,
  IconFileText,
  IconBell,
  IconRefresh,
  IconExternalLink,
} from '@tabler/icons-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';
import Link from 'next/link';

// Mock data - in production, this would come from your APIs
const mockData = {
  systemHealth: {
    overall: 98.5,
    services: [
      { name: 'Gateway', status: 'healthy', uptime: 99.9, responseTime: 45 },
      { name: 'Research', status: 'healthy', uptime: 98.2, responseTime: 120 },
      { name: 'Brand', status: 'healthy', uptime: 97.8, responseTime: 85 },
      { name: 'Content', status: 'warning', uptime: 95.5, responseTime: 200 },
      { name: 'Agent', status: 'healthy', uptime: 99.1, responseTime: 78 },
    ],
  },
  analytics: {
    totalRequests: 45692,
    totalUsers: 1247,
    documentsProcessed: 8934,
    mentionsMonitored: 23847,
    contentGenerated: 2156,
    agentsRunning: 42,
    trends: [
      { date: '2024-01-01', requests: 1200, users: 45, mentions: 890 },
      { date: '2024-01-02', requests: 1580, users: 52, mentions: 1200 },
      { date: '2024-01-03', requests: 1890, users: 61, mentions: 1450 },
      { date: '2024-01-04', requests: 2100, users: 58, mentions: 1680 },
      { date: '2024-01-05', requests: 1950, users: 67, mentions: 1520 },
      { date: '2024-01-06', requests: 2340, users: 73, mentions: 1890 },
      { date: '2024-01-07', requests: 2580, users: 79, mentions: 2100 },
    ],
    serviceUsage: [
      { service: 'Research', usage: 35, color: '#9c27b0' },
      { service: 'Brand', usage: 28, color: '#009688' },
      { service: 'Content', usage: 22, color: '#ff9800' },
      { service: 'Agent', usage: 15, color: '#673ab7' },
    ],
  },
  recentActivity: [
    { id: 1, type: 'research', message: 'Document "Market Analysis 2024" processed', time: '2 min ago' },
    { id: 2, type: 'brand', message: 'New mention detected with positive sentiment', time: '5 min ago' },
    { id: 3, type: 'content', message: 'Blog post "AI Trends" scheduled for publishing', time: '12 min ago' },
    { id: 4, type: 'agent', message: 'Workflow "Social Media Monitor" completed successfully', time: '18 min ago' },
    { id: 5, type: 'research', message: 'Knowledge graph updated with 47 new entities', time: '25 min ago' },
  ],
};

const StatCard = ({ title, value, change, icon: Icon, color, href }: {
  title: string;
  value: string | number;
  change?: { value: number; trend: 'up' | 'down' };
  icon: React.ComponentType<any>;
  color: string;
  href?: string;
}) => {
  const CardContent = (
    <Card withBorder p="lg" radius="md" className="hover-lift">
      <Group justify="space-between" align="flex-start">
        <div>
          <Text c="dimmed" size="sm" tt="uppercase" fw={700}>
            {title}
          </Text>
          <Text fw={700} size="xl" mt="xs">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </Text>
          {change && (
            <Group gap={4} mt="xs">
              {change.trend === 'up' ? (
                <IconArrowUp size="1rem" stroke={1.5} color="green" />
              ) : (
                <IconArrowDown size="1rem" stroke={1.5} color="red" />
              )}
              <Text size="sm" c={change.trend === 'up' ? 'green' : 'red'}>
                {change.value}%
              </Text>
              <Text size="sm" c="dimmed">
                vs last week
              </Text>
            </Group>
          )}
        </div>
        <ThemeIcon
          color={color}
          variant="light"
          size={60}
          radius="md"
        >
          <Icon size="2rem" stroke={1.5} />
        </ThemeIcon>
      </Group>
    </Card>
  );

  return href ? (
    <Link href={href} style={{ textDecoration: 'none' }}>
      {CardContent}
    </Link>
  ) : CardContent;
};

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setLoading(false), 1000);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh
    setTimeout(() => setRefreshing(false), 1000);
  };

  if (loading) {
    return (
      <Stack>
        <Group justify="space-between">
          <Skeleton height={32} width={200} />
          <Skeleton height={36} width={100} />
        </Group>
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} height={120} />
          ))}
        </SimpleGrid>
        <Grid>
          <Grid.Col span={{ base: 12, md: 8 }}>
            <Skeleton height={300} />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Skeleton height={300} />
          </Grid.Col>
        </Grid>
      </Stack>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Stack gap="xl">
        {/* Header */}
        <Group justify="space-between">
          <div>
            <Title order={1}>Dashboard</Title>
            <Text c="dimmed" size="lg">
              Welcome back! Here's what's happening with your AI platform.
            </Text>
          </div>
          <Button
            leftSection={<IconRefresh size="1rem" />}
            variant="light"
            onClick={handleRefresh}
            loading={refreshing}
          >
            Refresh
          </Button>
        </Group>

        {/* System Health Alert */}
        {mockData.systemHealth.overall < 95 && (
          <Alert color="orange" title="System Health Warning">
            Some services are experiencing issues. Check the service status below for details.
          </Alert>
        )}

        {/* Key Metrics */}
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3, lg: 6 }} spacing="lg">
          <StatCard
            title="Total Requests"
            value={mockData.analytics.totalRequests}
            change={{ value: 12.5, trend: 'up' }}
            icon={IconActivity}
            color="blue"
          />
          <StatCard
            title="Active Users"
            value={mockData.analytics.totalUsers}
            change={{ value: 8.2, trend: 'up' }}
            icon={IconUsers}
            color="green"
          />
          <StatCard
            title="Documents Processed"
            value={mockData.analytics.documentsProcessed}
            change={{ value: 15.3, trend: 'up' }}
            icon={IconFileText}
            color="violet"
            href="/dashboard/research"
          />
          <StatCard
            title="Brand Mentions"
            value={mockData.analytics.mentionsMonitored}
            change={{ value: 23.8, trend: 'up' }}
            icon={IconBrandTwitter}
            color="teal"
            href="/dashboard/brand"
          />
          <StatCard
            title="Content Generated"
            value={mockData.analytics.contentGenerated}
            change={{ value: 5.7, trend: 'up' }}
            icon={IconEdit}
            color="orange"
            href="/dashboard/content"
          />
          <StatCard
            title="Agents Running"
            value={mockData.analytics.agentsRunning}
            change={{ value: 3.2, trend: 'down' }}
            icon={IconRobot}
            color="grape"
            href="/dashboard/agents"
          />
        </SimpleGrid>

        <Grid>
          {/* Analytics Chart */}
          <Grid.Col span={{ base: 12, lg: 8 }}>
            <Card withBorder p="lg" radius="md">
              <Group justify="space-between" mb="md">
                <Title order={3}>Platform Activity</Title>
                <Badge variant="light" color="blue">
                  Last 7 days
                </Badge>
              </Group>
              <Box h={300}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={mockData.analytics.trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      formatter={(value, name) => [value.toLocaleString(), name.charAt(0).toUpperCase() + name.slice(1)]}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="requests" 
                      stroke="#2196f3" 
                      strokeWidth={2}
                      dot={{ fill: '#2196f3', strokeWidth: 2, r: 4 }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="mentions" 
                      stroke="#009688" 
                      strokeWidth={2}
                      dot={{ fill: '#009688', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </Card>
          </Grid.Col>

          {/* Service Usage */}
          <Grid.Col span={{ base: 12, lg: 4 }}>
            <Card withBorder p="lg" radius="md" h="100%">
              <Title order={3} mb="md">Service Usage</Title>
              <Stack gap="md">
                <Center>
                  <RingProgress
                    size={160}
                    thickness={8}
                    sections={mockData.analytics.serviceUsage.map((item) => ({
                      value: item.usage,
                      color: item.color,
                    }))}
                    label={
                      <Text size="xs" ta="center" px="xs" style={{ pointerEvents: 'none' }}>
                        Service<br />Distribution
                      </Text>
                    }
                  />
                </Center>
                <Stack gap="xs">
                  {mockData.analytics.serviceUsage.map((item) => (
                    <Group key={item.service} justify="space-between">
                      <Group gap="xs">
                        <Box
                          w={12}
                          h={12}
                          style={{ backgroundColor: item.color, borderRadius: 2 }}
                        />
                        <Text size="sm">{item.service}</Text>
                      </Group>
                      <Text size="sm" fw={500}>
                        {item.usage}%
                      </Text>
                    </Group>
                  ))}
                </Stack>
              </Stack>
            </Card>
          </Grid.Col>

          {/* System Health */}
          <Grid.Col span={{ base: 12, lg: 6 }}>
            <Card withBorder p="lg" radius="md">
              <Group justify="space-between" mb="md">
                <Title order={3}>System Health</Title>
                <Badge 
                  variant="filled" 
                  color={mockData.systemHealth.overall > 95 ? 'green' : 'orange'}
                >
                  {mockData.systemHealth.overall}% Healthy
                </Badge>
              </Group>
              <Stack gap="md">
                {mockData.systemHealth.services.map((service) => (
                  <Box key={service.name}>
                    <Group justify="space-between" mb="xs">
                      <Group gap="xs">
                        <Text size="sm" fw={500}>{service.name}</Text>
                        <Badge 
                          size="xs" 
                          variant="dot"
                          color={service.status === 'healthy' ? 'green' : service.status === 'warning' ? 'orange' : 'red'}
                        >
                          {service.status}
                        </Badge>
                      </Group>
                      <Group gap="md">
                        <Text size="xs" c="dimmed">{service.uptime}% uptime</Text>
                        <Text size="xs" c="dimmed">{service.responseTime}ms</Text>
                      </Group>
                    </Group>
                    <Progress 
                      value={service.uptime} 
                      color={service.status === 'healthy' ? 'green' : service.status === 'warning' ? 'orange' : 'red'}
                      size="sm"
                    />
                  </Box>
                ))}
              </Stack>
            </Card>
          </Grid.Col>

          {/* Recent Activity */}
          <Grid.Col span={{ base: 12, lg: 6 }}>
            <Card withBorder p="lg" radius="md">
              <Group justify="space-between" mb="md">
                <Title order={3}>Recent Activity</Title>
                <ActionIcon variant="subtle" size="sm">
                  <IconExternalLink size="1rem" />
                </ActionIcon>
              </Group>
              <Stack gap="md">
                {mockData.recentActivity.map((activity) => (
                  <Group key={activity.id} gap="md">
                    <ThemeIcon
                      size="sm"
                      variant="light"
                      color={
                        activity.type === 'research' ? 'violet' :
                        activity.type === 'brand' ? 'teal' :
                        activity.type === 'content' ? 'orange' : 'grape'
                      }
                    >
                      {activity.type === 'research' && <IconSearch size="0.8rem" />}
                      {activity.type === 'brand' && <IconBrandTwitter size="0.8rem" />}
                      {activity.type === 'content' && <IconEdit size="0.8rem" />}
                      {activity.type === 'agent' && <IconRobot size="0.8rem" />}
                    </ThemeIcon>
                    <div style={{ flex: 1 }}>
                      <Text size="sm">{activity.message}</Text>
                      <Text size="xs" c="dimmed">{activity.time}</Text>
                    </div>
                  </Group>
                ))}
              </Stack>
            </Card>
          </Grid.Col>
        </Grid>
      </Stack>
    </motion.div>
  );
}