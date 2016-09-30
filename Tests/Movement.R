
radians <- function(degrees) {
    degrees * pi / 180
}

Shift <- function(alpha) {
    m <- diag(4)
    m[1,4] <- alpha
    m
}

Slide <- function(alpha) {
    m <- diag(4)
    m[2,4] <- alpha
    m
}

Rise <- function(alpha) {
    m <- diag(4)
    m[3,4] <- alpha
    m
}

Twist <- function(alpha) {
    alpha <- radians(alpha)
    m <- diag(4)
    m[1,1] <- cos(alpha)
    m[1,2] <- -sin(alpha)
    m[2,1] <- sin(alpha)
    m[2,2] <- cos(alpha)
    m
}

Roll <- function(alpha) {
    alpha <- radians(alpha)
    m <- diag(4)
    m[1,1] <- cos(alpha)
    m[1,3] <- sin(alpha)
    m[3,1] <- -sin(alpha)
    m[3,3] <- cos(alpha)
    m
}

Tilt <- function(alpha) {
    alpha <- radians(alpha)
    m <- diag(4)
    m[2,2] <- cos(alpha)
    m[2,3] <- -sin(alpha)
    m[3,2] <- sin(alpha)
    m[3,3] <- cos(alpha)
    m
}

ADNA <- function() {
    return (Twist(31.1185909091) %*%
            Roll(2.06055181818)  %*%
            Tilt(2.12008054545)  %*%
            Rise(3.37983727273)  %*%
            Slide(-2.41029181818) %*% 
            Shift(-0.549621454545)
    )
}

BDNA <- function() {
    return (Twist(35.9063052632) %*%
            Roll(-2.66592947368) %*%
            Tilt(-1.80234789474) %*%
            Rise(3.27145684211) %*%
            Slide(-1.34487389474) %*%
            Shift(-0.425181378947))
}

print(ADNA())
print(BDNA())

