'use client';

import { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Title,
  Text,
  TextInput,
  PasswordInput,
  Button,
  Group,
  Stack,
  Anchor,
  Divider,
  Alert,
  LoadingOverlay,
  Box,
  Center,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import { notifications } from '@mantine/notifications';
import { IconMail, IconLock, IconAlertCircle, IconBrandGoogle, IconBrandGithub } from '@tabler/icons-react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { useAuthStore } from '@/lib/stores/auth';

interface LoginFormData {
  email: string;
  password: string;
}

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams?.get('redirect') || '/dashboard';

  const { login, isAuthenticated, error, clearError } = useAuthStore();

  const form = useForm<LoginFormData>({
    initialValues: {
      email: '',
      password: '',
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : 'Invalid email'),
      password: (value) => (value.length < 6 ? 'Password must be at least 6 characters' : null),
    },
  });

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !loading) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, loading, router, redirectTo]);

  // Clear error when component mounts or form changes
  useEffect(() => {
    clearError();
  }, [clearError]);

  const handleSubmit = async (values: LoginFormData) => {
    setLoading(true);
    clearError();

    try {
      const success = await login(values.email, values.password);

      if (success) {
        notifications.show({
          title: 'Welcome back!',
          message: 'You have been successfully logged in.',
          color: 'green',
          autoClose: 3000,
        });
        router.push(redirectTo);
      }
    } catch (err) {
      notifications.show({
        title: 'Login failed',
        message: 'Please check your credentials and try again.',
        color: 'red',
        autoClose: 5000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSocialLogin = (provider: 'google' | 'github') => {
    // TODO: Implement social login
    notifications.show({
      title: 'Coming Soon',
      message: `${provider.charAt(0).toUpperCase() + provider.slice(1)} login will be available soon.`,
      color: 'blue',
      autoClose: 3000,
    });
  };

  return (
    <Box
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
    >
      <Container size="xs">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Paper
            radius="lg"
            p="xl"
            withBorder
            style={{
              position: 'relative',
              backdropFilter: 'blur(20px)',
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            }}
          >
            <LoadingOverlay
              visible={loading}
              overlayProps={{ radius: 'lg' }}
              loaderProps={{ size: 'md' }}
            />

            {/* Logo and Title */}
            <Center mb="xl">
              <Stack align="center" gap="xs">
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.3, delay: 0.2 }}
                >
                  <Box
                    style={{
                      width: 60,
                      height: 60,
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #2196f3 0%, #9c27b0 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '24px',
                      fontWeight: 'bold',
                      color: 'white',
                    }}
                  >
                    P
                  </Box>
                </motion.div>
                <Title order={2} ta="center" className="gradient-text">
                  Plasma Engine
                </Title>
                <Text size="sm" ta="center" c="dimmed">
                  Welcome back to your AI platform
                </Text>
              </Stack>
            </Center>

            {/* Error Alert */}
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.2 }}
              >
                <Alert
                  icon={<IconAlertCircle size="1rem" />}
                  title="Login failed"
                  color="red"
                  mb="md"
                  variant="light"
                >
                  {error}
                </Alert>
              </motion.div>
            )}

            {/* Login Form */}
            <form onSubmit={form.onSubmit(handleSubmit)}>
              <Stack gap="md">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                >
                  <TextInput
                    label="Email"
                    placeholder="your@email.com"
                    size="md"
                    leftSection={<IconMail size="1.1rem" />}
                    {...form.getInputProps('email')}
                    styles={{
                      input: {
                        '&:focus': {
                          borderColor: '#2196f3',
                        },
                      },
                    }}
                  />
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 }}
                >
                  <PasswordInput
                    label="Password"
                    placeholder="Your password"
                    size="md"
                    leftSection={<IconLock size="1.1rem" />}
                    {...form.getInputProps('password')}
                    styles={{
                      input: {
                        '&:focus': {
                          borderColor: '#2196f3',
                        },
                      },
                    }}
                  />
                </motion.div>

                <Group justify="space-between" mt="md">
                  <Anchor component={Link} href="/auth/forgot-password" size="sm">
                    Forgot your password?
                  </Anchor>
                </Group>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.5 }}
                >
                  <Button
                    type="submit"
                    size="md"
                    fullWidth
                    loading={loading}
                    gradient={{ from: '#2196f3', to: '#9c27b0' }}
                    style={{
                      background: 'linear-gradient(135deg, #2196f3 0%, #9c27b0 100%)',
                    }}
                  >
                    Sign In
                  </Button>
                </motion.div>
              </Stack>
            </form>

            {/* Divider */}
            <Divider label="Or continue with" labelPosition="center" my="xl" />

            {/* Social Login */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.6 }}
            >
              <Group grow>
                <Button
                  variant="outline"
                  leftSection={<IconBrandGoogle size="1rem" />}
                  onClick={() => handleSocialLogin('google')}
                  size="md"
                >
                  Google
                </Button>
                <Button
                  variant="outline"
                  leftSection={<IconBrandGithub size="1rem" />}
                  onClick={() => handleSocialLogin('github')}
                  size="md"
                >
                  GitHub
                </Button>
              </Group>
            </motion.div>

            {/* Sign Up Link */}
            <Text ta="center" mt="xl">
              Don't have an account?{' '}
              <Anchor component={Link} href="/auth/register" fw={600}>
                Sign up
              </Anchor>
            </Text>
          </Paper>
        </motion.div>
      </Container>
    </Box>
  );
}