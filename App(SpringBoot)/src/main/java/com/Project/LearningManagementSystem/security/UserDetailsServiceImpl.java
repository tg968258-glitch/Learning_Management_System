package com.Project.LearningManagementSystem.security;

import com.Project.LearningManagementSystem.entity.User;
import com.Project.LearningManagementSystem.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserDetailsServiceImpl implements UserDetailsService {

    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String uid) throws UsernameNotFoundException {
        User user = userRepository.findById(uid)
            .orElseThrow(() -> new UsernameNotFoundException("User not found: " + uid));

        return new UserPrincipal(
            user.getUid(),
            user.getEmail(),
            user.getPasswordHash(),
            user.getRole(),
            user.isActive()
        );
    }
}
