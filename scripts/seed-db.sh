#!/bin/bash

# Seed database with sample data for testing

set -e

echo "🌱 Seeding database with sample data..."

# Wait for database to be ready
until docker-compose exec -T postgres pg_isready; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Insert sample data
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-showcaise_user} -d ${POSTGRES_DB:-showcaise} << EOF

-- Insert sample users
INSERT INTO users (email, password_hash) VALUES 
    ('demo@showcaise.com', 'hashed_password_demo'),
    ('test@showcaise.com', 'hashed_password_test')
ON CONFLICT (email) DO NOTHING;

-- Insert sample sessions
INSERT INTO sessions (id, user_id, video_filename, video_path, status) VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 1, 'demo_presentation.mp4', 'videos/demo/demo_presentation.mp4', 'completed')
ON CONFLICT (id) DO NOTHING;

-- Insert sample analysis results
INSERT INTO speech_analysis (session_id, transcript, wpm, filler_count, tone_score) VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 'This is a sample presentation transcript...', 145, 8, 72)
ON CONFLICT DO NOTHING;

INSERT INTO vision_analysis (session_id, eye_contact_score, posture_score, confidence_score) VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 68, 82, 75)
ON CONFLICT DO NOTHING;

-- Insert sample recommendations
INSERT INTO recommendations (session_id, recommendation, priority) VALUES
    ('123e4567-e89b-12d3-a456-426614174000', 'Reduce filler words by 40%', 1),
    ('123e4567-e89b-12d3-a456-426614174000', 'Maintain eye contact more consistently', 2),
    ('123e4567-e89b-12d3-a456-426614174000', 'Vary your tone more for emphasis', 3)
ON CONFLICT DO NOTHING;

EOF

echo "✅ Database seeded successfully!"
