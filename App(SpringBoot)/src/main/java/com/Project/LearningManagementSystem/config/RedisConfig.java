package com.Project.LearningManagementSystem.config;

import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.jsontype.impl.LaissezFaireSubTypeValidator;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.time.Duration;

import org.springframework.boot.autoconfigure.cache.RedisCacheManagerBuilderCustomizer;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializationContext.SerializationPair;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
@EnableCaching
public class RedisConfig {

    /*
     * Redis-specific ObjectMapper.
     *
     * IMPORTANT:
     * This is intentionally NOT a @Bean.
     *
     * Otherwise Spring MVC may use it for normal API request/response JSON
     * and start expecting the "@class" property.
     */
    private ObjectMapper createRedisObjectMapper() {

        ObjectMapper mapper = new ObjectMapper();

        mapper.registerModule(new JavaTimeModule());

        mapper.disable(
                SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

        mapper.configure(
                DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES,
                false);

        mapper.activateDefaultTyping(
                LaissezFaireSubTypeValidator.instance,
                ObjectMapper.DefaultTyping.NON_FINAL,
                JsonTypeInfo.As.PROPERTY);

        return mapper;
    }

    /*
     * Default Redis cache configuration
     */
    @Bean
    public RedisCacheConfiguration cacheConfiguration() {

        ObjectMapper redisObjectMapper = createRedisObjectMapper();

        GenericJackson2JsonRedisSerializer serializer = new GenericJackson2JsonRedisSerializer(
                redisObjectMapper);

        return RedisCacheConfiguration
                .defaultCacheConfig()
                .entryTtl(Duration.ofMinutes(10))
                .disableCachingNullValues()
                .serializeKeysWith(
                        SerializationPair.fromSerializer(
                                new StringRedisSerializer()))
                .serializeValuesWith(
                        SerializationPair.fromSerializer(
                                serializer));
    }

    /*
     * Different TTLs for different caches
     */
    @Bean
    public RedisCacheManagerBuilderCustomizer redisCacheManagerBuilderCustomizer(
            RedisCacheConfiguration cacheConfiguration) {

        return builder -> builder

                .withCacheConfiguration(
                        "courses",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "modules",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "lessons",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "lessonDetails",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "announcements",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(10)))

                .withCacheConfiguration(
                        "teachers",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(30)))

                .withCacheConfiguration(
                        "teacherProfiles",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "studentProfiles",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "quizzes",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)))

                .withCacheConfiguration(
                        "sessions",
                        cacheConfiguration.entryTtl(
                                Duration.ofMinutes(15)));
    }

    /*
     * RedisTemplate for manual Redis operations
     */
    @Bean
    public RedisTemplate<String, Object> redisTemplate(
            RedisConnectionFactory connectionFactory) {

        RedisTemplate<String, Object> template = new RedisTemplate<>();

        template.setConnectionFactory(connectionFactory);

        StringRedisSerializer stringSerializer = new StringRedisSerializer();

        ObjectMapper redisObjectMapper = createRedisObjectMapper();

        GenericJackson2JsonRedisSerializer jsonSerializer = new GenericJackson2JsonRedisSerializer(
                redisObjectMapper);

        template.setKeySerializer(
                stringSerializer);

        template.setHashKeySerializer(
                stringSerializer);

        template.setValueSerializer(
                jsonSerializer);

        template.setHashValueSerializer(
                jsonSerializer);

        template.afterPropertiesSet();

        return template;
    }
}