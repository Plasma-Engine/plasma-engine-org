'use client';

import { useState, useEffect } from 'react';
import {
  AppShell,
  Burger,
  Group,
  Text,
  UnstyledButton,
  Avatar,
  Menu,
  ActionIcon,
  Badge,
  Indicator,
  Skeleton,
  Stack,
  NavLink,
  ScrollArea,
  Divider,
  Box,
  Title,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import {
  IconDashboard,
  IconSearch,
  IconBrandTwitter,
  IconEdit,
  IconRobot,
  IconSettings,
  IconLogout,
  IconBell,
  IconSun,
  IconMoon,
  IconUser,
  IconChevronRight,
  IconActivity,
  IconDatabase,
} from '@tabler/icons-react';
import { useRouter, usePathname } from 'next/navigation';
import { useMantineColorScheme } from '@mantine/core';
import Link from 'next/link';
import { useAuthStore } from '@/lib/stores/auth';
import { checkServiceHealth } from '@/lib/api/client';

interface NavItem {
  label: string;
  icon: React.ComponentType<{ size?: string | number; stroke?: number }>;
  href: string;
  badge?: string;
  color?: string;
  children?: NavItem[];
}

const navigation: NavItem[] = [
  {
    label: 'Dashboard',
    icon: IconDashboard,
    href: '/dashboard',
    color: 'blue',
  },
  {
    label: 'Research',
    icon: IconSearch,
    href: '/dashboard/research',
    color: 'violet',
    children: [
      { label: 'Documents', icon: IconDatabase, href: '/dashboard/research/documents' },
      { label: 'Search', icon: IconSearch, href: '/dashboard/research/search' },
      { label: 'Knowledge Graph', icon: IconActivity, href: '/dashboard/research/knowledge-graph' },
    ],
  },
  {
    label: 'Brand Monitoring',
    icon: IconBrandTwitter,
    href: '/dashboard/brand',
    color: 'teal',
    children: [
      { label: 'Mentions', icon: IconBrandTwitter, href: '/dashboard/brand/mentions' },
      { label: 'Analytics', icon: IconActivity, href: '/dashboard/brand/analytics' },
      { label: 'Alerts', icon: IconBell, href: '/dashboard/brand/alerts' },
    ],
  },
  {
    label: 'Content',
    icon: IconEdit,
    href: '/dashboard/content',
    color: 'orange',
    children: [
      { label: 'Library', icon: IconDatabase, href: '/dashboard/content/library' },
      { label: 'Create', icon: IconEdit, href: '/dashboard/content/create' },
      { label: 'Calendar', icon: IconActivity, href: '/dashboard/content/calendar' },
    ],
  },
  {
    label: 'Agents',
    icon: IconRobot,
    href: '/dashboard/agents',
    color: 'grape',
    children: [
      { label: 'Workflows', icon: IconActivity, href: '/dashboard/agents/workflows' },
      { label: 'Automation', icon: IconRobot, href: '/dashboard/agents/automation' },
    ],
  },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mobileOpened, { toggle: toggleMobile }] = useDisclosure();
  const [desktopOpened, { toggle: toggleDesktop }] = useDisclosure(true);
  const [serviceHealth, setServiceHealth] = useState<Record<string, boolean>>({});
  const [loadingHealth, setLoadingHealth] = useState(true);

  const router = useRouter();
  const pathname = usePathname();
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  const { user, logout, isAuthenticated, isLoading } = useAuthStore();

  // Check service health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await checkServiceHealth();
        setServiceHealth(health);
      } catch (error) {
        console.error('Failed to check service health:', error);
      } finally {
        setLoadingHealth(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  const handleLogout = async () => {
    try {
      await logout();
      notifications.show({
        title: 'Logged out',
        message: 'You have been successfully logged out.',
        color: 'green',
        autoClose: 3000,
      });
      router.push('/auth/login');
    } catch (error) {
      notifications.show({
        title: 'Logout failed',
        message: 'There was an error logging you out.',
        color: 'red',
        autoClose: 5000,
      });
    }
  };

  const renderNavItems = (items: NavItem[], level = 0) => {
    return items.map((item) => (
      <Box key={item.href} mb={level === 0 ? 'xs' : 0}>
        <NavLink
          component={Link}
          href={item.href}
          label={item.label}
          leftSection={<item.icon size="1.2rem" stroke={1.5} />}
          rightSection={
            item.badge ? (
              <Badge size="xs" variant="filled" color={item.color}>
                {item.badge}
              </Badge>
            ) : item.children ? (
              <IconChevronRight size="0.8rem" stroke={1.5} />
            ) : null
          }
          active={pathname === item.href}
          variant="subtle"
          color={item.color}
          styles={{
            root: {
              borderRadius: '8px',
              marginBottom: level === 0 ? '4px' : '2px',
            },
          }}
        >
          {item.children && renderNavItems(item.children, level + 1)}
        </NavLink>
      </Box>
    ));
  };

  if (!isAuthenticated || isLoading) {
    return (
      <Box p="xl">
        <Stack>
          <Skeleton height={40} />
          <Skeleton height={300} />
        </Stack>
      </Box>
    );
  }

  const unhealthyServices = Object.entries(serviceHealth).filter(([_, healthy]) => !healthy);

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 280,
        breakpoint: 'sm',
        collapsed: { mobile: !mobileOpened, desktop: !desktopOpened },
      }}
      padding="md"
    >
      {/* Header */}
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={mobileOpened} onClick={toggleMobile} hiddenFrom="sm" size="sm" />
            <Burger opened={desktopOpened} onClick={toggleDesktop} visibleFrom="sm" size="sm" />
            <Group gap="xs">
              <Box
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #2196f3 0%, #9c27b0 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: 'white',
                }}
              >
                P
              </Box>
              <Title order={4} className="gradient-text">
                Plasma Engine
              </Title>
            </Group>
          </Group>

          <Group>
            {/* Service Health Indicator */}
            {!loadingHealth && (
              <Indicator
                color={unhealthyServices.length > 0 ? 'red' : 'green'}
                size={8}
                disabled={unhealthyServices.length === 0}
              >
                <ActionIcon
                  variant="subtle"
                  size="lg"
                  title={
                    unhealthyServices.length > 0
                      ? `${unhealthyServices.length} service(s) unhealthy`
                      : 'All services healthy'
                  }
                >
                  <IconActivity size="1.1rem" />
                </ActionIcon>
              </Indicator>
            )}

            {/* Notifications */}
            <ActionIcon variant="subtle" size="lg">
              <IconBell size="1.1rem" />
            </ActionIcon>

            {/* Theme Toggle */}
            <ActionIcon
              variant="subtle"
              size="lg"
              onClick={() => toggleColorScheme()}
              title="Toggle theme"
            >
              {colorScheme === 'dark' ? <IconSun size="1.1rem" /> : <IconMoon size="1.1rem" />}
            </ActionIcon>

            {/* User Menu */}
            <Menu shadow="md" width={200} position="bottom-end">
              <Menu.Target>
                <UnstyledButton>
                  <Group gap="xs">
                    <Avatar size={32} radius="xl" color="blue">
                      {user?.firstName?.[0]}{user?.lastName?.[0]}
                    </Avatar>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <Text size="sm" fw={500} truncate>
                        {user?.firstName} {user?.lastName}
                      </Text>
                      <Text size="xs" c="dimmed" truncate>
                        {user?.email}
                      </Text>
                    </div>
                  </Group>
                </UnstyledButton>
              </Menu.Target>

              <Menu.Dropdown>
                <Menu.Label>Account</Menu.Label>
                <Menu.Item leftSection={<IconUser size={14} />}>Profile</Menu.Item>
                <Menu.Item leftSection={<IconSettings size={14} />}>Settings</Menu.Item>

                <Menu.Divider />

                <Menu.Item
                  color="red"
                  leftSection={<IconLogout size={14} />}
                  onClick={handleLogout}
                >
                  Logout
                </Menu.Item>
              </Menu.Dropdown>
            </Menu>
          </Group>
        </Group>
      </AppShell.Header>

      {/* Navigation */}
      <AppShell.Navbar p="md">
        <AppShell.Section grow my="md" component={ScrollArea}>
          <div>{renderNavItems(navigation)}</div>
        </AppShell.Section>

        <Divider mb="md" />

        {/* Service Status */}
        <AppShell.Section>
          <Text size="xs" c="dimmed" mb="xs">
            Service Status
          </Text>
          <Stack gap={4}>
            {Object.entries(serviceHealth).map(([service, healthy]) => (
              <Group key={service} justify="space-between">
                <Text size="xs" tt="capitalize">
                  {service}
                </Text>
                <Badge
                  size="xs"
                  variant="dot"
                  color={healthy ? 'green' : 'red'}
                >
                  {healthy ? 'Online' : 'Offline'}
                </Badge>
              </Group>
            ))}
          </Stack>
        </AppShell.Section>
      </AppShell.Navbar>

      {/* Main Content */}
      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  );
}